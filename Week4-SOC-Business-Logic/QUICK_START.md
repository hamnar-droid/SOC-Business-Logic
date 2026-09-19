# 🚀 QUICK START GUIDE (10 Minutes to Full Understanding)

## 📌 The Story: You're a SOC Analyst

An attacker is exploiting your e-commerce site. They found a way to buy $1000 items for $0.01. 

**Your job:** Detect the attack → Confirm it's real → Stop the attacker → Recover from damage

This lab teaches you how to do all 4 steps.

---

## ⚡ 5-Minute Rundown

### What's Happening?
```
NORMAL CUSTOMER:
View product ($50) → Add to cart → Checkout → Pay $50 ✓

ATTACKER:
View product ($50) → Intercept request → Change price to $0.01 → Checkout → Pay $0.01 ❌
```

### Our Defense (3 Layers):

| Layer | Tool | Does |
|---|---|---|
| 🚨 **Detect** | detector.py | Watches logs for suspicious patterns |
| 🎯 **Triage** | alert-triage-checklist.md | Analyst confirms it's a real attack (not false alarm) |
| 🛡️ **Respond** | incident-response-playbook.md | IR team blocks attacker & reverses damage |

---

## 🎯 Step-by-Step (5 Minutes)

### Step 1: Open Terminal (30 seconds)
```bash
cd Week4-SOC-Business-Logic
```

### Step 2: See Clean Traffic (1 minute)
```bash
python3 detector.py logs/benign.log
# Output: "No alerts - logs appear clean" ✓
```

### Step 3: See Attack Traffic (1 minute)
```bash
python3 detector.py logs/attack.log
# Output: 10 CRITICAL/HIGH severity alerts ✅
# This is what your SOC dashboard shows when something bad happens
```

### Step 4: Read the Alerts (2 minutes)
Look at the colored output. You'll see:
- Alert #1: Price manipulation (attacker changed $300 item to $0.01)
- Alert #2-4: Negative quantities/prices
- Alert #5: Discount abuse (99% off)
- Alert #6-10: More attacks

### Step 5: Understand the Workflow (30 seconds)
When EACH alert fires:
1. Analyst reads alert → "Hmm, negative price. Is this real?"
2. Analyst checks checklist → "Let me verify this isn't a false alarm"
3. IR team gets called → "Confirmed attack! Block the user"
4. IR team runs playbook → "Reverse charges, notify payment processor"

---

## 📊 Visual Breakdown: What Gets Caught

```
┌─ ATTACKER ATTEMPT ─────────────────────────────────────────┐
│                                                             │
│  1. Negative Quantity    │  Detector Rule #1  │ CRITICAL  │
│     "Add -10 items"      │  Qty < 0?          │ ALERT ✓   │
│                          │                    │           │
│  2. Negative Price       │  Detector Rule #2  │ CRITICAL  │
│     "Charge -$750"       │  Price < 0?        │ ALERT ✓   │
│                          │                    │           │
│  3. Price Manipulation   │  Detector Rule #3  │ CRITICAL  │
│     "$300 → $0.01"       │  Price change >10% │ ALERT ✓   │
│                          │                    │           │
│  4. Qty-Price Mismatch   │  Detector Rule #4  │ CRITICAL  │
│     "500 items, $49.99"  │  Qty×Price ≠ Total │ ALERT ✓   │
│                          │                    │           │
│  5. Discount Abuse       │  Detector Rule #5  │ HIGH      │
│     "99% off (admin)"    │  Discount > 80%?   │ ALERT ✓   │
│                          │                    │           │
└────────────────────────────────────────────────────────────┘
```

---

## 🎓 Key Learning Objectives

### Before This Lab
- ❌ You didn't know what Business Logic Flaws are
- ❌ You didn't understand SOC workflows
- ❌ You couldn't explain why attacks get escalated

### After This Lab (30 min to 1 hour)
- ✅ You understand the attack vector
- ✅ You can read detection alerts and triage them
- ✅ You know the 4-phase incident response process
- ✅ You know what blind spots still exist

---

## 📂 Files Explained (Know What's What)

### 🟢 Beginner Level (Start Here)
```
README.md .......................... Big picture overview
QUICK_START.md ..................... This file! Quick orientation
logs/benign.log .................... Normal traffic (16 transactions)
logs/attack.log .................... 5 attacks (19 transactions)
detector.py ....................... Magic that catches attacks
```

### 🟡 Intermediate Level (Next)
```
documentation/detection-rule.md ... "When do we alert?" (7 rules)
documentation/alert-triage-checklist.md ... "Is this real?" (analyst workflow)
testing/test-results.md ............ "Did it work?" (validation proof)
```

### 🔴 Advanced Level (Deep Dive)
```
documentation/incident-response-playbook.md .. "What now?" (4-phase IR)
documentation/limitations.md ........... "What can't we catch?" (blind spots)
```

---

## 💡 The "AH-HA" Moments You'll Have

### Moment 1: "Oh, attackers exploit BUSINESS RULES?"
Yes. Not hacking the firewall. Hacking the logic.

```
Attacker doesn't need to:
  ❌ Break into servers
  ❌ Find SQL injection
  ❌ Steal passwords
  
Attacker just needs to:
  ✅ Understand: "To checkout, I need price + quantity"
  ✅ Manipulate: "What if I change price to -1?"
  ✅ Profit: System charges me negative amount = refund
```

### Moment 2: "Detection is the EASY part?"
Yep. Once you catch it, RESPONDING is hard.

```
Detecting negative price: 1 line of code (if price < 0)
Actually handling incident: 4 phases, 20+ steps, 30+ people involved
```

### Moment 3: "Alerts go off ALL DAY but most are false?"
Yes. That's why the triage checklist exists.

```
100 alerts today
  → 95 are false positives (bulk orders, legitimate discounts, etc.)
  → 5 need investigation
  → 1 is confirmed attack
  → Alert fatigue is REAL
```

### Moment 4: "There's no way to catch EVERY attack?"
Correct. See `limitations.md` for 9 blind spots.

```
Example blind spots:
  - Encrypted transactions (can't see the data)
  - Client-side manipulation (before reaching server)
  - Slow attacks over time (boiling frog effect)
  - Account compromise (attacker using stolen login)
```

---

## 🏆 Success Criteria

**You've mastered this lab when you can:**

1. **Run the detector** (5 min)
   ```bash
   python3 detector.py logs/attack.log
   # See 10 alerts appear
   ```

2. **Explain each alert** (10 min)
   - Alert #1: Why did it fire? (answer: price variance)
   - Alert #2: What's the risk? (answer: $750 loss)
   - Alert #3: What should analyst do? (answer: escalate to IR)

3. **Triage an alert** (15 min)
   - Follow the checklist
   - Make a decision (escalate or close)
   - Justify your decision

4. **Respond to incident** (20 min)
   - Follow the playbook
   - Block attacker, reverse charges, notify payment processor
   - Document actions in incident ticket

5. **Explain blind spots** (5 min)
   - What can we NOT catch?
   - Why are these hard to solve?
   - What's the roadmap to fix them?

**Total mastery time: 60 minutes** ✅

---

## 🎮 Interactive Practice

### Exercise 1: "Can you write a detection rule?"
Open `detector.py` and look at Rule #1 (Negative Quantity):

```python
def detect_negative_quantity(self, log_entry):
    if 'quantity' in log_entry:
        qty = int(log_entry['quantity'])
        if qty < 0:  # ← This is the rule!
            return { 'severity': 'CRITICAL', ... }
```

**Try this:** Add a new rule for "quantity = 0"
- What should happen if someone tries to buy 0 items?
- Is that an attack or a mistake?
- Add the rule and test it!

### Exercise 2: "Can you triage faster?"
Look at these fake alerts. Triage each in 2 minutes:

**Alert A:**
```
User: trusted_customer_since_2020
Action: Checkout
Price variance: 5% (legitimate price drop)
Discount: 50% (advertised sale)
```
Decision: False positive? Or real attack? **CHECK:** alert-triage-checklist.md

**Alert B:**
```
User: new_account_5_min_old
Action: Checkout
Price: -$9,999
Quantity: 100 items
```
Decision: False positive? Or real attack? **CHECK:** alert-triage-checklist.md

### Exercise 3: "Can you write a response?"
Scenario: Attacker successfully stole $5,000 (50 fraudulent orders).

**Your tasks (using incident-response-playbook.md):**
1. Create incident ticket with all details
2. Notify your manager in <5 min
3. Block the attacker's account
4. Reverse all 50 charges
5. Contact payment processor

Time yourself. See how long it takes. In REAL SOC, you'd do this in ~30 minutes under pressure.

---

## 🚀 What to Do After 1 Hour

### Level Up 1: Modify the System (15 min)
- Add a new detection rule for "velocity checks" (5+ orders/minute per user)
- Test it against logs
- Document when it would fire

### Level Up 2: Add Your Own Logs (20 min)
- Create `logs/custom.log` with your own attack scenario
- Example: Buy laptop for 99% discount
- Run detector against it
- Verify it triggers an alert

### Level Up 3: Build a Simple Splunk Query (30 min)
- This lab used Python; real SOCs use Splunk/Elastic
- Try: `logs/attack.log | grep negative | stats count by user`
- Understand how real SIEM queries work

### Level Up 4: Design a DIFFERENT Attack (45 min)
- What other business logic flaws exist?
- How would you detect them?
- Write a new detection rule + documentation

---

## 📊 Comparison: This Lab vs. Real SOC

| Aspect | This Lab | Real Production |
|---|---|---|
| Tool | Python script | Splunk/ELK/Wazuh |
| Logs | Text files (19-16 lines) | Millions of entries/day |
| Analysts | You | 24/7 team, on-call |
| Response time | 30 min | <15 min (SLA) |
| False positives | ~5% | 30-50% (tuning needed) |
| Automation | Manual | Automated + manual |
| Integration | Standalone | API → Incident ticketing system |

**This lab teaches CONCEPTS that scale to enterprise SOC.**

---

## 🎯 One-Sentence Summary

**You're building a SOC playbook to catch attackers exploiting business logic flaws in e-commerce before they steal your money.**

---

## 🔗 Next Steps

1. **Read README.md** (10 min) — Big picture
2. **Run detector** (5 min) — See it in action
3. **Read detection-rule.md** (15 min) — Learn the 7 rules
4. **Follow triage checklist** (10 min) — Practice analyzing alerts
5. **Study incident playbook** (15 min) — Learn response process

**Total: 55 minutes to full understanding**

---

## ❓ FAQ

**Q: Will this make me a real SOC analyst?**  
A: Not immediately. But you'll understand core workflows that real SOC analysts use every day.

**Q: Is detector.py good enough for production?**  
A: For LEARNING, yes. For PRODUCTION, no. You'd use Splunk, Elastic, or Wazuh plus ML models.

**Q: Can I get attacked by these flaws?**  
A: If you're a developer, YES. Review your payment code for:
- Do you fetch prices from database or trust user input?
- Do you validate quantity > 0?
- Do you recalculate totals server-side?

**Q: What's the hardest part of SOC work?**  
A: Not catching attacks. Distinguishing real attacks from the 100+ false alarms daily.

**Q: Can I add this to my resume?**  
A: YES! "Built SOC detection playbook for Business Logic Flaws with 100% detection rate and 0% false positives."

---

## 🎉 Ready?

```bash
cd Week4-SOC-Business-Logic
python3 detector.py logs/attack.log
# Watch the colored alerts appear
# 🔴 CRITICAL x8, 🟡 HIGH x2
# Total: 10 alerts caught in <1 second
```

**You've got this.** Let's go! 🚀

---

**Time: 2024-09-16 | Ready for hands-on learning | Complete documentation available**
