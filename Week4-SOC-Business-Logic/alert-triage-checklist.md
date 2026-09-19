# Alert Triage Checklist: Business Logic Flaw

**Purpose:** Standardized workflow for SOC analysts to rapidly assess and prioritize incoming Business Logic Flaw alerts.

**Time Estimate:** 3-5 minutes per alert (high severity), 5-10 minutes (medium severity)

---

## IMMEDIATE ACTIONS (First 60 Seconds)

### [ ] 1. Confirm Alert is Real
- [ ] Check if alert triggered in last 5 minutes (recent activity)
- [ ] Verify log entry exists in SIEM
- [ ] Confirm it's not a duplicate/duplicate alert noise
- [ ] Note timestamp: `____________`

**Decision Tree:**
- **If alert is stale (>1 hour old):** Skip to "Archived Analysis" section, move to LOW priority
- **If alert is recent & confirmed:** Proceed to next step

---

### [ ] 2. Assess Severity & Blast Radius

| Alert Type | Severity | Affected Resources | Time to Impact |
|---|---|---|---|
| Negative Quantity | CRITICAL | User account, Order, Payment | Immediate |
| Negative Price | CRITICAL | Payment, Revenue, User account | Immediate |
| Price Manipulation | CRITICAL | Multiple orders/users | Minutes |
| Qty-Price Mismatch | CRITICAL | Inventory, Revenue | Hours |
| Extreme Discount Abuse | HIGH | Revenue, Discount system | Hours |
| Total Mismatch | HIGH | Accounting, Fraud detection | Hours |

**Your assessment:**
- Alert Type: `____________`
- Severity Level: `[ ] CRITICAL [ ] HIGH [ ] MEDIUM`
- Estimated affected orders: `____________`

**Decision:**
- **CRITICAL + Unknown blast radius:** Escalate to Incident Response immediately (see escalation matrix)
- **HIGH + Isolated user:** Continue triage, escalate if pattern detected
- **MEDIUM + Known user:** Continue triage

---

## TIER 1 TRIAGE (2-3 minutes)

### [ ] 3. Identify the User & Account Status

**Look up user in system:**
```
User ID: ________________
Email: ________________
Account created: ________________
Account status: [ ] Active [ ] Flagged [ ] Previous fraud [ ] Trusted
Previous alerts: [ ] Yes [ ] No  If yes, count: ____
```

**Check account history:**
- [ ] First time this user? (→ Suspicious for rare attack patterns like negative qty)
- [ ] Known good customer? (→ Less suspicious; could be support test)
- [ ] Repeat offender? (→ Escalate immediately)

**Decision:**
- **New account + CRITICAL alert:** HIGH SUSPICION → Escalate
- **Trusted account + CRITICAL alert:** MEDIUM SUSPICION → Continue investigation
- **Any account + MEDIUM alert:** LOW SUSPICION → Continue triage

---

### [ ] 4. Examine the Transaction Details

**Extract from alert/logs:**
```
Order ID: ________________
Product(s): ________________
Quantity (view): ________________ → Quantity (checkout): ________________
Price (view): $____________ → Price (checkout): $____________
Total charged: $____________
Expected total: $____________
Discount applied: ________________ (____________%)
Payment method: [ ] Credit Card [ ] PayPal [ ] Other
Payment status: [ ] Approved [ ] Declined [ ] Pending
```

**Calculate the deviation:**
- Expected total: `$____________`
- Actual charged: `$____________`
- Loss amount: `$____________`
- **If loss > $500:** HIGH PRIORITY (escalate)
- **If loss > $5,000:** CRITICAL (escalate immediately)

---

### [ ] 5. Check for Known False Positive Patterns

**Does this match a known benign pattern?**

- [ ] Legitimate return/refund (negative qty in return system)
  - *Action:* Check if order is in "RMA" or "Returns" queue
  - If YES → **Classify as FALSE POSITIVE**, close alert
  
- [ ] Bulk/wholesale order with tiered pricing
  - *Action:* Check if order qualifies for bulk discount
  - If YES (qty > 50 AND discount policy allows) → **Classify as FALSE POSITIVE**, close alert

- [ ] Known promotional campaign (>80% discount)
  - *Action:* Check marketing calendar for active flash sales
  - If YES (campaign active + discount code whitelisted) → **Classify as FALSE POSITIVE**, close alert

- [ ] Multi-currency rounding error (<1% variance)
  - *Action:* Convert to base currency, recalculate
  - If variance <1% → **Classify as FALSE POSITIVE**, close alert

- [ ] Test transaction (staging/sandbox data)
  - *Action:* Check if user IP is in developer/test network
  - If YES → **Classify as FALSE POSITIVE**, escalate to dev team

**If ANY of above match:**
- [ ] Document false positive reason: `____________`
- [ ] Close alert with comment
- [ ] **SKIP to "Closing the Alert" section**

**If NONE of above match:**
- [ ] Proceed to Tier 2 investigation

---

## TIER 2 INVESTIGATION (3-5 minutes)

### [ ] 6. Examine Network & Behavioral Context

**Check access patterns:**
```
User IP: ________________
IP geolocation: ________________
User's normal country: ________________
VPN/Proxy detected: [ ] Yes [ ] No
Device fingerprint: ________________
Previous IP addresses used: ________________
```

**Behavioral red flags:**
- [ ] IP from high-risk country/region?
- [ ] VPN/proxy used (but not normal for this user)?
- [ ] New device/browser fingerprint?
- [ ] Rapid geographic changes (e.g., USA → China in 2 hours)?
- [ ] Multiple failed login attempts before this transaction?

**Decision:**
- **3+ behavioral red flags:** HIGH SUSPICION → Escalate
- **1-2 red flags:** MEDIUM SUSPICION → Request user verification
- **No red flags:** LOW SUSPICION → Continue analysis

---

### [ ] 7. Check Request/Response Integrity

**Examine HTTP logs (if available):**
- [ ] Request headers match normal user profile?
- [ ] Any header manipulation detected (User-Agent spoofing)?
- [ ] Request body size/complexity unusual?
- [ ] Response status codes: `____________`
- [ ] Any 40x (client) errors before successful transaction?

**Check for tampering indicators:**
- [ ] Burst of requests in short time window (possible bot)?
- [ ] Cookie manipulation attempted (session fixation)?
- [ ] Duplicate request IDs (replay attack)?
- [ ] Timezone mismatch (client vs. server)?

**Decision:**
- **Evidence of tampering:** CONFIRMED ATTACK → Escalate immediately
- **Suspicious but inconclusive:** MEDIUM SUSPICION → Request additional logs

---

### [ ] 8. Correlate with Other Systems

**Check upstream security systems:**
- [ ] WAF (Web Application Firewall) logs for this user/IP?
  - [ ] No alerts: Normal ✓
  - [ ] Alerts: Review them (possible coordinated attack)
  
- [ ] IDS (Intrusion Detection) alerts?
- [ ] Rate limiting triggered?
- [ ] DDoS detected on payment endpoint around this time?

**Check fraud detection system (if integrated):**
- [ ] 3D Secure (payment verification) passed? [ ] Yes [ ] No
- [ ] Velocity checks passed? (How many transactions in last hour?)
  - Normal: 1-3 | Suspicious: 5+ in 1 hour
- [ ] Device risk score: `____________` (0=safe, 100=blocked)
- [ ] Amount-based rules triggered?

---

## ESCALATION MATRIX

### When to Escalate Immediately (to Incident Response Team)

**ESCALATE if ANY of these conditions are TRUE:**

- [ ] **Negative quantity OR negative price** (automatic CRITICAL)
- [ ] **Estimated loss > $5,000**
- [ ] **Confirmed tampering/MITM attack**
- [ ] **Evidence of account compromise** (unauthorized access)
- [ ] **Pattern detected:** 3+ similar alerts from different users in 24 hours
- [ ] **Discount code abuse:** Code used 10+ times in 1 hour
- [ ] **Attack validated against multiple systems** (WAF + IDS + fraud detection)

**Escalation Process:**
1. [ ] Create incident ticket: `TICKET #: ____________`
2. [ ] Notify Incident Response Lead (Slack/phone)
3. [ ] Attach all logs, screenshots, and analysis to ticket
4. [ ] Request immediate action:
   - [ ] Block user account
   - [ ] Reverse transaction
   - [ ] Review payment processor records
   - [ ] Check for lateral movement in account

---

## CLOSING THE ALERT

### [ ] 9. Document Your Analysis

**Choose one outcome:**

### **Outcome A: Confirmed Malicious Activity**
```
Status: ESCALATED TO INCIDENT RESPONSE
Ticket: ____________
Confidence: [ ] High [ ] Medium [ ] Low
Reasoning: ____________________________________________________
Recommended Action: Block user | Reverse payment | Notify payment processor
```

### **Outcome B: Suspicious but Inconclusive**
```
Status: ESCALATED FOR MANUAL REVIEW
Assigned to: ____________
Confidence: Low-Medium
Reasoning: ____________________________________________________
Recommended Action: Request user verification | Review historical activity
Required follow-up: [ ] Within 4 hours [ ] Within 24 hours
```

### **Outcome C: False Positive**
```
Status: CLOSED
False Positive Reason: [ ] Legitimate return [ ] Bulk discount [ ] Campaign [ ] Test [ ] Other
Details: ____________________________________________________
Action taken: Whitelist pattern [ ] Yes [ ] No
```

---

## QUICK REFERENCE: Decision Tree

```
ALERT TRIGGERED
    ↓
[1] Is alert recent (< 1 hour)? 
    NO → Archive, low priority
    YES ↓
[2] Is loss > $5,000?
    YES → Escalate immediately
    NO ↓
[3] Is user known fraud offender?
    YES → Escalate immediately
    NO ↓
[4] Is this a known false positive pattern?
    YES → Close alert, document
    NO ↓
[5] Are there 3+ behavioral red flags?
    YES → Escalate for verification
    NO ↓
[6] Is there evidence of tampering?
    YES → Escalate immediately
    NO ↓
[7] Do 3+ users show same pattern today?
    YES → Escalate (possible attack campaign)
    NO ↓
[8] Request user verification (email/phone)
    User confirms transaction → Close alert
    User denies transaction → Escalate immediately
```

---

## Template: Alert Summary Report

**Copy this template into incident ticket:**

```
BUSINESS LOGIC FLAW ALERT SUMMARY
═════════════════════════════════════════════════════════
Alert Type: ________________
Severity: [ ] CRITICAL [ ] HIGH [ ] MEDIUM
Time Detected: ________________
User ID: ________________
Order ID: ________________

QUICK FACTS:
- Expected total: $____________
- Actual total: $____________
- Loss amount: $____________
- Attack vector: [ ] Negative qty [ ] Price manipulation [ ] Discount abuse [ ] Other

CONFIDENCE LEVEL: [ ] High (≥80%) [ ] Medium (50-80%) [ ] Low (<50%)

ANALYST NOTES:
________________________________________________________________
________________________________________________________________

RECOMMENDED ACTION:
[ ] Block account
[ ] Reverse transaction
[ ] Notify payment processor
[ ] Contact user
[ ] Monitor for pattern
[ ] Whitelist (false positive)

Analyzed by: ____________ | Time spent: ____ min | Status: ____________
```

---

## Performance Metrics (Track These)

- **MTTD** (Mean Time to Detect): How fast we flag alerts
- **MTTR** (Mean Time to Respond): How fast we triage & escalate
- **False Positive Rate**: Percentage of alerts that are benign
- **Detection Coverage**: Percentage of actual attacks we catch

**Target SLAs:**
- CRITICAL alerts: Triage within 5 minutes
- HIGH alerts: Triage within 15 minutes
- FALSE POSITIVES: Identify within 3 minutes
