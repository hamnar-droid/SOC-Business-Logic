# Business Logic Flaw Detection Rule Documentation

## Overview
This document describes 7 detection rules designed to identify Business Logic Flaw attacks targeting e-commerce and payment systems. These attacks exploit gaps in business logic to manipulate prices, quantities, and calculations.

---

## Rule 1: Negative Quantity Detection
**Severity:** CRITICAL  
**CVSS Score:** 9.1

### What It Detects
Attempts to add negative quantities to orders—a classic refund-without-purchase exploit.

### Log Pattern
```
action=add_to_cart | quantity=-10 | ...
action=checkout | total_items=-10 | ...
```

### Attack Example
- Attacker views item (price: $75)
- Adds `-10` items to cart instead of `+10`
- System calculates: `-10 × $75 = -$750` (attacker receives $750)
- Attacker checks out with negative total

### Detection Rule
```python
IF quantity < 0:
    ALERT("NEGATIVE_QUANTITY", severity="CRITICAL")
```

### False Positives
- Legitimate refund/return processing (typically flagged differently in logs)
- Test transactions with negative values for validation

### Tuning
- Monitor refund processing logs separately
- Whitelist legitimate return order IDs if quantity can be negative in that context

---

## Rule 2: Negative Price Detection
**Severity:** CRITICAL  
**CVSS Score:** 9.1

### What It Detects
Attempts to charge negative amounts—the system owes the attacker money instead.

### Log Pattern
```
price=-99.99 | ...
total_price=-4999.50 | ...
```

### Attack Example
- Attacker intercepts payment request
- Changes price from `$199.99` to `-$199.99`
- System processes as credit instead of charge
- Attacker gains merchandise + refund

### Detection Rule
```python
IF price < 0 OR total_price < 0:
    ALERT("NEGATIVE_PRICE", severity="CRITICAL")
```

### False Positives
- Rare; prices should never be negative in legitimate transactions
- Only exception: accounting adjustments (clearly marked in logs)

### Tuning
- Zero false positive tolerance—any negative price is malicious
- Monitor payment gateway rejection logs for attempts

---

## Rule 3: Price Manipulation Detection
**Severity:** CRITICAL  
**CVSS Score:** 8.9

### What It Detects
Significant price changes between product view and checkout (MITM or intercept attack).

### Log Pattern
```
action=view_product | price=299.99 | ...
action=intercept_request | price=0.01 | ...
action=checkout | total_price=0.05 | ...
```

### Attack Example
- Attacker views $300 item
- Intercepts checkout request
- Modifies price to $0.01
- Receives $300 item for 1 penny

### Detection Rule
```python
IF checkout_price != view_price:
    price_variance = abs(checkout_price - view_price) / view_price
    IF price_variance > 10%:  # More than 10% change
        ALERT("PRICE_MANIPULATION", severity="CRITICAL")
```

### False Positives
- Legitimate price drops (monitored separately)
- Sales/promotions applied at checkout (discount code flags instead)
- Tax recalculations (<5% variance acceptable)

### Tuning
- Set threshold to 10% price variance
- Exclude promotion codes from this rule (Rule 5 handles discounts)

---

## Rule 4: Quantity-Price Mismatch
**Severity:** CRITICAL  
**CVSS Score:** 9.0

### What It Detects
User orders N items but pays for 1 (cart/session manipulation).

### Log Pattern
```
action=add_to_cart | quantity=500 | ...
action=checkout | total_items=500 | total_price=49.99 | ...  # Should be $24,995
```

### Attack Example
- Attacker adds 500 items to cart ($49.99 each)
- Manipulates session/cookies to reduce quantity in checkout calculation
- Checkout shows 500 items but charges for 1 item ($49.99 instead of $24,995)

### Detection Rule
```python
expected_total = total_items × unit_price
IF abs(actual_total - expected_total) > 5% variance:
    IF total_items > 100:  # Additional check: bulk orders
        ALERT("QUANTITY_PRICE_MISMATCH", severity="CRITICAL")
```

### False Positives
- Shipping discounts on bulk orders
- Tiered pricing (e.g., "buy 100+ get 50% off")
- Coupons applied at checkout

### Tuning
- Whitelist known bulk discount campaigns
- Require >5% variance + >100 item threshold to reduce false positives

---

## Rule 5: Extreme Discount Abuse
**Severity:** HIGH  
**CVSS Score:** 7.8

### What It Detects
Abnormally high discounts (>80%) applied during checkout—possible discount code enumeration or admin access abuse.

### Log Pattern
```
action=apply_discount | discount_code=ADMIN99 | discount_pct=99 | ...
action=checkout | total_price=$1.30 | ...  # 100 items, 99% off
```

### Attack Example
- Attacker enumerates discount codes (brute force)
- Finds "ADMIN99" = 99% off
- Applies during checkout
- Receives items for pennies

### Detection Rule
```python
IF discount_pct > 80:
    ALERT("EXTREME_DISCOUNT", severity="HIGH")
    flag_discount_code_for_review(discount_code)
```

### False Positives
- Legitimate admin testing codes (should be flagged in test environment only)
- Limited-time flash sales (>80% off)
- Loyalty rewards for high-value customers

### Tuning
- Whitelist known promotional codes
- Separate alerts for: test codes vs. real discounts
- Monitor discount code usage frequency (rapid reuse = suspicious)

---

## Rule 6: Total Calculation Mismatch
**Severity:** HIGH  
**CVSS Score:** 7.5

### What It Detects
Order total doesn't match `quantity × unit_price` (possible rounding exploit or system bug).

### Log Pattern
```
total_items=3 | price=75.00 | total_price=180.00  # Should be 225.00
```

### Attack Example
- Order: 100 items × $9.99 each = $999.00
- Attacker manipulates calculation
- System charges $99.90 (off by 10×)

### Detection Rule
```python
expected = total_items × price
variance = abs(actual_total - expected) / expected
IF variance > 5%:  # More than 5% variance
    ALERT("TOTAL_CALCULATION_MISMATCH", severity="HIGH")
```

### False Positives
- Rounding errors (<1%)
- Tax/fee adjustments
- Multi-currency conversions

### Tuning
- Set threshold to 5% variance (accounts for rounding)
- Whitelist orders with documented fee structures

---

## Rule 7: Anomaly/Risk Flag Detection
**Severity:** CRITICAL / HIGH

### What It Detects
Explicit ANOMALY or RISK flags already in logs—catches pre-tagged suspicious activity.

### Log Pattern
```
action=checkout | RISK=price_manipulation | ...
action=add_to_cart | ANOMALY=negative_total | ...
```

### Detection Rule
```python
IF log_entry.ANOMALY or log_entry.RISK:
    ALERT(log_entry.ANOMALY or log_entry.RISK, severity=CRITICAL/HIGH)
```

### Use Case
- Upstream security tools (WAF, proxy, app logging) have flagged suspicious activity
- Second-layer validation in SOC workflow

---

## Detection Rule Matrix

| Rule | Trigger | Severity | False Pos. Risk | MTTR |
|------|---------|----------|-----------------|------|
| Negative Quantity | qty < 0 | CRITICAL | Very Low | 5 min |
| Negative Price | price < 0 | CRITICAL | Very Low | 5 min |
| Price Manipulation | price_variance > 10% | CRITICAL | Medium | 15 min |
| Quantity-Price Mismatch | qty×price variance > 5% | CRITICAL | High | 20 min |
| Extreme Discount | discount > 80% | HIGH | High | 10 min |
| Total Mismatch | calc_variance > 5% | HIGH | Medium | 15 min |
| Anomaly Flags | RISK/ANOMALY in log | Variable | Low | 5 min |

---

## Tuning Recommendations

### Phase 1: High Confidence (Week 1-2)
- Enable: Rules 1, 2, 7 (negative qty/price, explicit flags)
- Expected FP rate: <2%

### Phase 2: Medium Confidence (Week 2-4)
- Enable: Rule 3 (price manipulation, 10% threshold)
- Enable: Rule 6 (total mismatch, 5% threshold)
- Expected FP rate: 5-10%

### Phase 3: All Rules (Week 4+)
- Enable: Rule 4 (quantity mismatch, requires >100 items)
- Enable: Rule 5 (discount abuse, whitelist known codes)
- Review & tune thresholds monthly
- Expected FP rate: 5-15%

---

## Known Blind Spots & Limitations

See `limitations.md` for gaps in this detection approach.
