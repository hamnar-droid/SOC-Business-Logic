# Incident Response Playbook: Business Logic Flaw Attack

**Scope:** Confirmed Business Logic Flaw attacks (price/quantity manipulation)  
**Duration:** 0-4 hours (initial response + containment)  
**Stakeholders:** SOC, Incident Response, Finance, Customer Service, Engineering  

---

## PHASE 1: DETECTION & ALERTING (0-15 minutes)

### Step 1.1: Immediate Verification
- [ ] Confirm alert is NOT a false positive (see triage checklist)
- [ ] Verify attack vector: (check all that apply)
  - [ ] Negative quantity
  - [ ] Negative price
  - [ ] Price manipulation
  - [ ] Quantity-price mismatch
  - [ ] Discount abuse
- [ ] Calculate confirmed loss: `$____________`
- [ ] Identify affected user: `user_id: ____________`
- [ ] List all affected orders: `____________`

### Step 1.2: Create Incident Ticket
```
INCIDENT TICKET TEMPLATE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ticket ID: SEC-2024-BLFL-001         [Auto-generated]
Title: Business Logic Flaw - Price Manipulation [user_id]
Severity: CRITICAL
Status: OPEN
Created: [Timestamp]
Assigned to: Incident Response Lead

Summary:
[Brief description of attack]

Affected Orders: [List]
Estimated Loss: $[Amount]
User Account Status: [Active/Flagged]
```

### Step 1.3: Notify Key Stakeholders (Parallel)

**Immediate notification (within 5 minutes):**
- [ ] Incident Response Lead (email + Slack)
- [ ] Security Manager (email)
- [ ] Finance/Fraud team (email)

**Template message:**
```
URGENT: Business Logic Flaw Attack Detected

User: [user_id]
Order(s): [order_ids]
Loss: $[amount]
Attack Type: [type]
Status: Containment in progress

Full details in ticket: [link]
```

---

## PHASE 2: CONTAINMENT (15-45 minutes)

### Step 2.1: Block Attacker Account
**Severity: CRITICAL - Execute immediately**

**Actions:**
- [ ] Set user account status to `SUSPENDED`
- [ ] Revoke all active sessions for this user
- [ ] Add user email/IP to blocklist
- [ ] Notify payment processor to flag account

**Command (Example):**
```sql
UPDATE users SET status='SUSPENDED', suspended_reason='Security - Business Logic Attack' 
WHERE user_id='[attacker_id]';

UPDATE sessions SET is_valid=FALSE 
WHERE user_id='[attacker_id]';
```

**Verification:**
- [ ] User cannot login (test)
- [ ] Previous sessions terminated
- [ ] Account flagged in internal systems

### Step 2.2: Reverse Fraudulent Transactions
**Severity: CRITICAL - Execute within 30 minutes**

**For each affected order:**

**If payment NOT yet settled:**
```sql
UPDATE orders SET status='CANCELLED', cancel_reason='Fraud reversal' 
WHERE order_id IN ([list]);

UPDATE payments SET status='REFUNDED', refund_amount=amount, refund_timestamp=NOW()
WHERE order_id IN ([list]);

-- Restore inventory
UPDATE inventory SET quantity=quantity + [qty]
WHERE product_id IN ([affected_products]);
```

**If payment ALREADY settled:**
- [ ] Contact payment processor (see Step 2.4)
- [ ] Initiate chargeback/reversal request
- [ ] Update order status to `REFUND_IN_PROGRESS`

**Verification:**
- [ ] All affected orders show `CANCELLED` or `REFUND_IN_PROGRESS`
- [ ] Inventory levels restored
- [ ] Customer's payment method credited (if applicable)

**Communication to customer (if not attacker):**
```
[If legitimate customer affected by same flaw]

Subject: Order [order_id] - Security Action Required

We detected unauthorized modifications to your order. Your payment has been 
reversed and the order cancelled as a precaution. Your funds will return to 
your account within 3-5 business days.

If you have questions, please contact [support email].
```

### Step 2.3: Review & Patch Application Code
**Severity: HIGH - Start immediately, complete within 24 hours**

**Identify vulnerable code areas:**
- [ ] Price calculation logic (where unit_price gets overwritten)
- [ ] Quantity validation (negative/zero checks missing?)
- [ ] Discount application (does validation happen AFTER discount?)
- [ ] Checkout process (do you re-fetch product prices from DB?)
- [ ] Session/request handling (are you trusting client-submitted values?)

**Key questions to ask developers:**
```
1. Where does the final price/quantity come from in checkout?
   - From database (SAFE) or from form submission (VULNERABLE)?

2. Are price/quantity validated before calculating total?
   - Schema validation? (e.g., price > 0, quantity > 0)

3. Do you re-fetch product info from DB or trust cached client values?

4. Is discount validation separate from price calculation?
   - Discount applied to DB price (SAFE) or to user-submitted price (VULNERABLE)?

5. Are negative values explicitly rejected?
   - if (price < 0 || quantity < 0) { reject(); }?
```

**Example vulnerable code:**
```python
# VULNERABLE - trusts user input
@app.route('/checkout', methods=['POST'])
def checkout():
    user_price = request.form['price']        # ATTACKER CONTROLLED
    quantity = request.form['quantity']       # ATTACKER CONTROLLED
    total = user_price * quantity             # DIRECTLY CALCULATED
    charge_customer(user_id, total)           # CHARGES WRONG AMOUNT
```

**Example safe code:**
```python
# SAFE - fetches from DB
@app.route('/checkout', methods=['POST'])
def checkout():
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    
    # VALIDATE
    if quantity <= 0:
        return error("Invalid quantity")
    
    # FETCH from DB (authoritative source)
    product = db.query(Product).get(product_id)
    unit_price = product.price  # NOT from user input
    
    # RECALCULATE
    total = unit_price * quantity
    
    # VALIDATE AGAIN
    if total < 0 or total > MAX_ORDER_VALUE:
        return error("Invalid order total")
    
    charge_customer(user_id, total)
```

**Immediate fixes (within 1 hour):**
- [ ] Add strict input validation: `if price < 0 or quantity < 0: REJECT`
- [ ] Add server-side re-fetch of prices from DB (don't trust client)
- [ ] Log all price/quantity changes for audit trail
- [ ] Add explicit whitelist checks for discounts

**Testing (before deploying):**
- [ ] Test with quantity = -1 (should reject)
- [ ] Test with price = $0.01 (should use DB value)
- [ ] Test with negative total (should reject)
- [ ] Verify all old-protection code is in place

### Step 2.4: Contact Payment Processor
**Severity: HIGH - Execute within 30 minutes**

**Required information to have ready:**
- Fraudulent order IDs
- Transaction IDs from payment processor
- Amounts charged
- User's payment method
- Timeline of attack

**Communication template:**
```
Subject: URGENT: Fraud Report - Business Logic Flaw Attacks

We have detected unauthorized charges resulting from a business logic 
vulnerability in our application. We are taking immediate action:

DETAILS:
- Transaction IDs: [list]
- Amounts: [list]
- Attack method: Price manipulation via request interception
- Status: Charges reversed, application patched

REQUESTED ACTIONS:
1. Flag these transactions in your fraud detection system
2. Confirm reversal timeline for customer refunds
3. Alert us if you see similar patterns from other merchants
4. Review our integration for security gaps

Contact: [incident response lead phone/email]
Timeline: Response needed within 1 hour
```

**Typical response:**
- Reversals: 3-5 business days
- Prevention: May add additional verification requirements
- Chargeback liability: Depends on processor agreement

---

## PHASE 3: INVESTIGATION & FORENSICS (30 minutes - 4 hours)

### Step 3.1: Forensic Log Analysis
**Preserve evidence immediately:**

- [ ] Export all logs related to attacker (before log rotation)
- [ ] Capture network traffic (if available)
- [ ] Screenshot all SIEM/payment processor records
- [ ] Back up database before any deletion

**Questions to answer:**
```
Timeline Analysis:
- When did attacker first register account? ____________
- When was first attack attempt? ____________
- How many successful attacks? ____________
- Is attack still ongoing? ____________

Attack Pattern Analysis:
- Did attacker test with small amounts first? ____________
- Escalation path: (e.g., $5 → $50 → $500) ____________
- How did attacker discover this vulnerability? ____________
- Was this opportunistic or targeted reconnaissance? ____________

Access Pattern Analysis:
- Single IP address or multiple? ____________
- Consistent user agent? ____________
- Use of VPN/proxy? ____________
- Any failed login attempts before success? ____________
```

### Step 3.2: Identify All Affected Orders
**Critical for assessing full impact:**

**Query to find similar patterns:**
```sql
-- Find all orders where total ≠ (quantity × price)
SELECT order_id, user_id, total_items, price, total_price, 
       (total_items * price) as expected_total,
       ABS(total_price - (total_items * price)) as variance
FROM orders
WHERE timestamp > [attack_start_time]
  AND ABS(total_price - (total_items * price)) > (total_items * price * 0.05)
ORDER BY variance DESC;

-- Find all orders with negative values
SELECT * FROM orders
WHERE total_price < 0 OR total_items < 0
  AND timestamp > [48_hours_ago];

-- Find all excessive discounts
SELECT order_id, user_id, discount_pct, discount_amount, final_price
FROM orders
WHERE discount_pct > 80
  AND timestamp > [24_hours_ago]
ORDER BY discount_pct DESC;
```

**Results Summary:**
- [ ] Total orders affected: `____`
- [ ] Total loss amount: `$____`
- [ ] Total customers affected: `____`
- [ ] Number of attacker accounts: `____`

### Step 3.3: Determine Root Cause
**Select all that apply:**

- [ ] Price trusting client submission instead of DB
- [ ] Quantity validation not implemented
- [ ] Discount applied to user-submitted price (not DB price)
- [ ] Missing negative value checks
- [ ] Session hijacking (attacker modified cookie/token)
- [ ] Insufficient input validation on all fields
- [ ] Calculation error in price/quantity logic
- [ ] Race condition in checkout process

**Risk Rating of Vulnerability:**
- [ ] CRITICAL: Anyone can exploit (requires no special knowledge)
- [ ] HIGH: Moderate difficulty to exploit
- [ ] MEDIUM: Requires technical knowledge

---

## PHASE 4: RECOVERY & COMMUNICATION (1-4 hours)

### Step 4.1: Notify Affected Customers (If Any)
**If legitimate customer funds were stolen:**

**Communication:**
```
Subject: Important Security Update - Your Account [#ref]

We detected and stopped a security incident that may have affected your account.

WHAT HAPPENED:
A vulnerability in our system allowed an attacker to manipulate order totals. 
This did not affect legitimate customers' funds.

WHAT WE'RE DOING:
✓ Attacker account has been suspended
✓ All fraudulent charges have been reversed
✓ System vulnerability has been patched
✓ Enhanced monitoring is now in place

YOUR ACTION REQUIRED:
1. Change your password (if you use our platform)
2. Review your recent orders to ensure accuracy
3. Contact us immediately if you see any unauthorized charges

SUPPORT:
Email: [security team email]
Phone: [support phone]
Chat: [support chat link]

We take security seriously and apologize for this incident.
```

**Send to:**
- [ ] All customers affected by the attack
- [ ] Customers with accounts created in same timeframe as attacker
- [ ] All customers who checked out in past 48 hours (precaution)

### Step 4.2: Brief Public Statement (PR)
**Only if:**
- [ ] Attack affected >100 customers
- [ ] Attack resulted in >$10,000 loss
- [ ] Story likely to become public

**Statement template:**
```
[COMPANY] STATEMENT ON SECURITY INCIDENT

On [DATE], [COMPANY] detected and remediated a business logic vulnerability 
in our payment processing system.

INCIDENT DETAILS:
- Scope: [X orders across Y customer accounts]
- Timeline: [Start] to [End]
- Impact: [~$X loss; all reversed]
- Root cause: [Insufficient input validation on price/quantity fields]

ACTIONS TAKEN:
- Immediately suspended attacker account and reversed all fraudulent charges
- Deployed security patch to fix vulnerability
- Notified affected customers directly
- Launched comprehensive security review

CUSTOMER PROTECTION:
- No customer data (names, emails, payment details) was compromised
- All fraudulent charges have been refunded
- Customers are not liable for any charges

GOING FORWARD:
- Committed to enhanced code review for payment logic
- Implementing automated security testing for business logic flaws
- Third-party security audit scheduled for [DATE]

Questions? Contact: [security contact]
```

### Step 4.3: Update Status & Close Incident
**After containment & communication:**

**Final incident summary:**
```
INCIDENT CLOSURE REPORT
═════════════════════════════════════════════════════════
Incident ID: SEC-2024-BLFL-001
Duration: [Start] to [End] (__ hours)
Status: CLOSED

IMPACT ASSESSMENT:
- Direct loss: $[amount]
- Remediation cost: $[amount]
- Customer impact: [X affected]
- Reputational impact: [Low/Medium/High]

ROOT CAUSE:
[Description of vulnerability]

RESOLUTION:
✓ Application patched
✓ Attacker blocked
✓ Charges reversed
✓ Customers notified
✓ Payment processor coordinated

PREVENTION (Future):
[List changes made to prevent recurrence]

FOLLOW-UP ACTIONS:
[ ] Post-incident review meeting (scheduled: _______)
[ ] Third-party security audit (scheduled: _______)
[ ] Threat model update
[ ] Security training for dev team

Closed by: ____________ | Date: ____________
```

---

## PREVENTION CHECKLIST (After Incident)

**Implement these controls:**

### Code-Level Controls
- [ ] Input validation library (e.g., Marshmallow, Cerberus)
- [ ] Server-side re-fetch of all prices from database
- [ ] Explicit negative value rejection: `if (value < 0) reject()`
- [ ] Unit tests for edge cases: qty=0, qty=-1, price=-0.01, etc.
- [ ] Code review requirement for all payment logic changes

### Application-Level Controls
- [ ] Rate limiting on checkout endpoint (max 5 orders/min per user)
- [ ] Logging of ALL price/quantity changes (immutable audit log)
- [ ] Amount sanity checks (max order value, min product price)
- [ ] Double-entry verification (calculate total 2 different ways, compare)

### Infrastructure Controls
- [ ] Web Application Firewall (WAF) rules for price manipulation patterns
- [ ] Request signing (HMAC) to detect tampering
- [ ] Content Security Policy (CSP) to prevent injection
- [ ] API rate limiting & throttling

### Monitoring Controls
- [ ] Alert if same user has >5 orders/hour
- [ ] Alert if order total < expected by >10%
- [ ] Alert on any negative price/quantity
- [ ] Dashboard for business logic anomalies (unusual discounts, bulk orders)

### Incident Response Controls
- [ ] Documented playbook (this document) kept up-to-date
- [ ] Quarterly tabletop exercises simulating BL attacks
- [ ] On-call incident response contact list
- [ ] Automated response triggers (block user, reverse charge, alert team)

---

## Communication Tree

**Escalation path during incident:**

```
SOC Analyst detects alert
    ↓
Notifies Incident Response Lead (5 min)
    ↓
IR Lead escalates to:
  - Security Manager (email)
  - Finance/Fraud team (email)
  - Engineering lead (phone)
    ↓
If loss > $5,000:
  - CTO (phone)
  - CFO (phone)
  - Legal team (email)
    ↓
If loss > $50,000:
  - CEO (phone)
  - Public relations team (prepare statement)
  - Notify payment processor (urgent call)
```

**Contact List (Template):**

| Role | Name | Email | Phone | On-Call? |
|------|------|-------|-------|----------|
| Incident Response Lead | [Name] | [Email] | [Phone] | [ ] |
| Security Manager | [Name] | [Email] | [Phone] | [ ] |
| Finance/Fraud Lead | [Name] | [Email] | [Phone] | [ ] |
| Engineering Lead | [Name] | [Email] | [Phone] | [ ] |
| CTO | [Name] | [Email] | [Phone] | [ ] |
| Payment Processor Contact | [Name] | [Email] | [Phone] | [ ] |

---

## Lessons Learned (Post-Incident)

**Template for team debrief (within 48 hours of closure):**

1. **What went well?**
   - Alert triggered immediately
   - Response was coordinated across teams
   - [Other]

2. **What could be improved?**
   - Detection took X minutes (target: <5 min)
   - Triage checklist missing X step
   - [Other]

3. **Why did this happen?**
   - Root cause: [Insufficient input validation]
   - Contributing factors: [No security code review, lack of testing]

4. **What's the permanent fix?**
   - Code change: [Re-fetch prices from DB]
   - Process change: [Add security review to checkout changes]
   - Monitoring: [Alert on price/qty anomalies]

5. **Training needed?**
   - Dev team: [Secure coding for payment logic]
   - QA team: [Testing for business logic flaws]
   - SOC team: [Triage checklist update]

---

## References & Escalation Procedures

**Related Documents:**
- [Detection Rule Documentation](detection-rule.md)
- [Alert Triage Checklist](alert-triage-checklist.md)
- [Known Blind Spots](limitations.md)

**External Resources:**
- OWASP: Business Logic Vulnerabilities
- CWE-841: Improper Enforcement of Behavioral Workflow
- PCI DSS Requirement 6.5.10: Business Logic Flaws
