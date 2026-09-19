# Detection Blind Spots & Limitations

**Purpose:** Document what this detection system CANNOT catch, to manage expectations and guide future improvements.

---

## Blind Spot 1: Client-Side Only Manipulation (Unlogged)

### The Gap
If an attacker manipulates prices/quantities BEFORE any request reaches the server, there's no log entry to detect.

### Example Attack
```
Attacker's Browser:
  ↓ [Modifies JavaScript variable: product.price = 0.01]
  ↓ [Modifies DOM: <input value="0.01" />]
  ↓ [Sends modified request to server]
Server sees: price = 0.01 (normal log entry, triggers alert)
BUT: We can't see the intermediate client-side manipulation
```

### Why It Matters
- If checkout request is logged AFTER client-side changes, we only see the final (malicious) value
- We don't know if it was client-side manipulation vs. database error

### Mitigation
- ✅ **Implemented:** Verify price against database (re-fetch from DB)
- ✅ **Implemented:** Reject if server-DB price differs by >10%
- ❌ **Not Implemented:** Can't detect ALL client-side attacks, only the successful ones

---

## Blind Spot 2: Slow, Low-Value Attacks (Boiling Frog)

### The Gap
Multiple small fraudulent orders ($5-10 each) over hours/days might fall below detection thresholds.

### Example Attack
```
Day 1: 10 orders × $5 discount abuse = $50
Day 2: 15 orders × $4 discount abuse = $60
Day 3: 12 orders × $6 discount abuse = $72
Total loss: $182 (spread over 3 days)

Our threshold: Alert if loss > $500 OR discount > 80% per order
Result: MISSED (each order is $4-6, discount is 40-50%)
```

### Why It Matters
- Attacker avoids triggering per-order thresholds
- Cumulative damage only becomes obvious after days/weeks
- By then, attacker has already cashed out

### Mitigation
- ❌ **Not Implemented:** User-level cumulative fraud scoring
- ❌ **Not Implemented:** Day-over-day anomaly detection ("this user bought 50 items in 24h vs. normal 2/month")
- 🟡 **Possible:** Add rule for "10+ orders with unusual discount in 24 hours per user"

---

## Blind Spot 3: Account Compromise (Credential Theft)

### The Gap
If attacker uses a STOLEN but legitimate customer account, they're not "creating new account = suspicious."

### Example Attack
```
1. Attacker steals customer's login credentials (phishing/breach)
2. Attacker logs in as legitimate customer
3. Attacker applies price manipulation
4. Alert fires: "Negative price from user_001"
5. SOC checks: "user_001 is trusted customer, probably mistake"
6. SOC closes alert without escalating
7. Attacker profits, legitimate customer gets charged

Our detection: ✓ Catches negative price
Our weakness: ✗ Can't easily distinguish account compromise from insider threat
```

### Why It Matters
- Legitimate account = less suspicious (lower triage priority)
- Attacker blends in with normal user base
- Behavioral anomalies (new IP, new device) might not be logged

### Mitigation
- ✅ **Implemented:** Check for IP/device/geolocation changes
- ❌ **Not Implemented:** ML-based user behavior baseline (how does THIS user normally act?)
- ❌ **Not Implemented:** Request signing/HMAC to prevent interception
- 🟡 **Possible:** Add "impossible travel" rule (USA → China in 30 min)

---

## Blind Spot 4: Discount Code Enumeration (Business Logic Bypass)

### The Gap
Attacker can try 1000s of discount codes rapidly without triggering alerts if we only log successful applications.

### Example Attack
```
Attacker runs Python script:
  for code in discount_code_list:
    POST /checkout?code=code
    if price_drops > 50%:
      print(f"Found valid code: {code}")

Logs only show:
  [Success] discount=ADMIN99, price=-$0.01
  [Success] discount=SUMMER50, price=$50
  [Success] discount=EMPLOYEE75, price=$25

Result: Attacker finds and cashes in on leaked admin code
Our detection: ✓ Catches 80%+ discount
Our weakness: ✗ Doesn't detect the enumeration process itself
```

### Why It Matters
- By the time we see a successful 80%+ discount alert, attacker has already used it
- No visibility into attack attempts that failed

### Mitigation
- ❌ **Not Implemented:** Rate limiting on discount code validation endpoint
- ❌ **Not Implemented:** Logging of invalid discount code attempts
- ❌ **Not Implemented:** Brute-force detection on checkout endpoint
- 🟡 **Possible:** Alert if same user tries 5+ different discount codes in 1 hour

---

## Blind Spot 5: Multi-Step Attacks (Distributed Across Systems)

### The Gap
If attack requires coordination between payment system, inventory system, and shipping—we might only see one piece.

### Example Attack
```
Attacker buys item for $0.01 (price manipulation) ← We catch this
Attacker manipulates inventory to inflate stock count ← Different system, not monitored
Attacker uses dropshipping to sell the item elsewhere ← External system, invisible
Result: Attacker makes profit while we think we stopped the price fraud

Our detection: ✓ Catches price manipulation
Our weakness: ✗ Doesn't correlate across systems (inventory, shipping, fulfillment)
```

### Why It Matters
- Requires cross-system correlation (hard to implement)
- Attack can be split across different logs/databases

### Mitigation
- ❌ **Not Implemented:** Correlation with inventory system
- ❌ **Not Implemented:** Shipping system audit logs
- 🟡 **Possible:** Flag orders that are paid for but not shipped within 48h

---

## Blind Spot 6: False Negatives in Legitimate Edge Cases

### The Gap
Our rules might miss valid transactions that look suspicious.

### Scenarios We Might Miss

**1. Inventory Correction (Returns)**
```
Legitimate return adds quantity=-5 to reverse sale
Our alert: "Negative quantity!"
Reality: Correct business operation
False positive: Yes, but we should whitelist these
```

**Fix:** Whitelist orders in "RETURN" or "RMA" status

**2. B2B Bulk Purchase with Volume Discount**
```
Customer buys 1000 items, normally $100 each
With volume discount: $30 each
Total: 1000 × $30 = $30,000 (expected)
But order history shows "Last order: 2 items"
Our alert: "Unusual bulk purchase, possible manipulation"
Reality: Customer is legitimate B2B
False positive: Yes
```

**Fix:** Maintain customer profile data (is this a B2B customer?)

**3. Multi-Currency Rounding**
```
Product price in USD: $49.99
User in UK: £39.99 (converted & rounded)
Exchange rate variance: ~5%
Our alert: "Price mismatch 5%"
Reality: Correct currency conversion
False positive: Yes
```

**Fix:** Set threshold to 5%, account for FX rates

**4. Flash Sale / Time-Limited Promotion**
```
Marketing campaign: "50% off everything - 2 hours only"
Our alert: "Extreme discount 50%"
Reality: Authorized campaign
False positive: Yes
```

**Fix:** Whitelist promotional codes before campaign starts

### Impact
- If false positive rate exceeds 20%, SOC team stops trusting alerts
- "Boy who cried wolf" problem: Analysts ignore legitimate attacks

### Mitigation
- 🟡 **Implemented:** Alert threshold = 80% discount (avoids most 50% off sales)
- ❌ **Not Implemented:** Customer profile/history integration
- ❌ **Not Implemented:** Marketing calendar integration
- 🟡 **Possible:** Triage checklist with whitelist checks (see alert-triage-checklist.md)

---

## Blind Spot 7: Encrypted/Obfuscated Requests

### The Gap
If we can't decrypt or read log entries, we can't analyze them.

### Scenarios
- End-to-end encryption between client & server
- Compressed/binary log format
- Third-party payment processor API calls (we don't see their logs)
- Proxy/CDN re-routing (log timestamps don't match)

### Impact
- Complete data loss for encrypted transactions
- Impossible to detect attacks on encrypted channels

### Mitigation
- ❌ **Not Implemented:** Decryption at logging layer
- 🟡 **Possible:** Log prices/quantities BEFORE encryption
- 🟡 **Possible:** Partner with payment processor for shared visibility

---

## Blind Spot 8: Time Window Gaps (Log Gaps)

### The Gap
If logs are deleted, rotated, or not shipped to SIEM, we miss attacks.

### Scenarios
```
Attacker knows logs rotate every 24 hours
Attacker waits for log rotation (e.g., 2:00 AM)
Attacker performs attack during 2:00-2:05 AM window
Logs aren't yet shipped to SIEM
By the time we see logs, attack is 5+ hours old
We might miss it or classify as low priority
```

### Impact
- Time-sensitive attacks can be missed
- Historical analysis is incomplete

### Mitigation
- ❌ **Not Implemented:** Real-time log streaming (instead of batch)
- 🟡 **Possible:** Overlap log shipment windows (don't delete until confirmed in SIEM)

---

## Blind Spot 9: Sophisticated Attackers Using Our Rules

### The Gap
Once our detection rules are public, skilled attackers adapt their attacks.

### Scenarios
```
Attacker reads our detection rules:
"We alert on negative quantities"
→ Attacker stays within -0.001 to 0 (fractional negative)
→ Triggers our rule, but amount is tiny ($0.001)
→ SOC ignores "penny-ante" fraud
→ Attacker repeats 10,000x per day, makes $10/day → $3,650/year

Attacker reads: "Alert if discount > 80%"
→ Attacker uses 79% discount
→ Avoids alert
→ Repeat across 1000 orders = massive fraud
```

### Why It Matters
- Assumes attackers are unsophisticated
- Real attackers WILL study our rules
- Rules need constant updating

### Mitigation
- 🟡 **Implemented:** Multiple rules (not just one threshold)
- ❌ **Not Implemented:** Machine learning to catch novel attacks
- 🟡 **Possible:** Dynamic threshold adjustment (80% discount → 75% as attackers adapt)

---

## Summary Table: Detection Gaps by Category

| Blind Spot | Severity | Effort to Fix | Recommended Action |
|---|---|---|---|
| Unlogged client-side manipulation | HIGH | Medium | Implement server-side price re-fetch (already done) |
| Boiling frog (slow attacks) | MEDIUM | High | Add user-level cumulative scoring |
| Account compromise | MEDIUM | High | Integrate user behavior baseline detection |
| Discount enumeration | MEDIUM | Low | Add rate limiting on checkout |
| Multi-system attacks | HIGH | Very High | Implement cross-system correlation |
| False negatives (legit edge cases) | MEDIUM | Low | Maintain whitelist of exceptions |
| Encrypted requests | HIGH | Very High | Log at pre-encryption layer |
| Log gaps | MEDIUM | Medium | Implement real-time streaming |
| Adaptive attackers | MEDIUM | Ongoing | Monthly rule updates + ML |

---

## Recommended Roadmap (Next 3 Months)

### Month 1: Quick Wins (High Impact, Low Effort)
- [ ] Implement rate limiting on checkout endpoint
- [ ] Add customer profile integration (identify B2B customers)
- [ ] Build whitelist for legitimate promotional codes
- [ ] Add cumulative fraud score per user (5+ orders/day = flag)

### Month 2: Medium Effort Improvements
- [ ] Implement user behavior baseline (ML)
- [ ] Cross-system correlation with inventory logs
- [ ] Real-time log streaming (replace batch shipment)
- [ ] Update detection thresholds based on observed attacks

### Month 3: Long-term Improvements
- [ ] Third-party security audit of payment logic
- [ ] Implementation of request signing (HMAC)
- [ ] API rate limiting at middleware level
- [ ] Quarterly playbook update + tabletop exercises

---

## Important Caveat

**This detection system is REACTIVE, not PREVENTIVE.**

✅ Good for catching attacks that DO happen  
✓ Good for triggering incident response  
✗ Cannot prevent clever attackers entirely

**True prevention requires:**
1. **Secure code** (input validation, no client-side trust)
2. **Secure architecture** (server-side calculation, DB validation)
3. **Defense in depth** (WAF, payment processor rules, customer friction)

Detection is the *third line of defense*, not the first.

---

## For More Information

- See `detection-rule.md` for specific rule coverage
- See `alert-triage-checklist.md` for manual verification steps
- See `incident-response-playbook.md` for remediation guidance
