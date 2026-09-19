# Week 4 SOC: Business Logic Flaw Detection Playbook

## 🎯 Overview

A complete, production-ready **Security Operations Center (SOC)** defense system for detecting and responding to **Business Logic Flaw attacks** (price/quantity manipulation). Built without a complex SIEM—just Python, sample logs, and clear documentation.

**Perfect for:** Cybersecurity students learning SOC workflows, analysts practicing incident response, security engineers building defense playbooks.

---

## 📋 What's Included

### 1. **Detection Engine** (`detector.py`)
- Simple Python script that parses logs and applies 7 detection rules
- Catches: negative quantities, negative prices, price manipulation, discount abuse, quantity-price mismatches
- Real-time color-coded alerts (red = CRITICAL, yellow = HIGH)
- JSON output for integration with other tools

### 2. **Sample Logs**
- `logs/benign.log` — Normal e-commerce transactions (clean baseline)
- `logs/attack.log` — 5 realistic attack scenarios with fraud attempts
- Both tested against detector with 0% false positives + 100% attack detection

### 3. **Documentation** (Complete Playbooks)

| Document | Purpose | Audience |
|---|---|---|
| **detection-rule.md** | 7 detection rules with CVSS scores, tuning guidance, false positive analysis | Security Engineers, SOC Leads |
| **alert-triage-checklist.md** | Step-by-step workflow for analysts to assess & prioritize alerts | SOC Analysts |
| **incident-response-playbook.md** | 4-phase containment & remediation guide (detect → contain → investigate → recover) | Incident Response Team |
| **limitations.md** | 9 documented blind spots + roadmap to fix them | Security Leaders, Architects |

### 4. **Test Results** (`testing/test-results.md`)
- Validation that detector catches all attacks
- Proof of 0% false positives on legitimate traffic
- Performance metrics & coverage analysis

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Download & Explore
```bash
cd Week4-SOC-Business-Logic
ls -la
# You should see: logs/, documentation/, testing/, detector.py, README.md
```

### Step 2: Run Detection on Clean Traffic
```bash
python3 detector.py logs/benign.log
# Should output: "No alerts - logs appear clean" ✓
```

### Step 3: Run Detection on Attack Traffic
```bash
python3 detector.py logs/attack.log
# Should output: 10 alerts across 5 attackers (CRITICAL + HIGH severity)
```

### Step 4: Read the Alert Output
Look at the colored output—this is what a SOC analyst sees:
- 🔴 **CRITICAL** alerts (8) = Immediate escalation
- 🟡 **HIGH** alerts (2) = Priority investigation

### Step 5: Open Documentation
```bash
# Start with this (5 min read)
cat documentation/detection-rule.md | head -50

# Then this (10 min read - most important)
cat documentation/alert-triage-checklist.md | head -100

# Deep dive (20 min read)
cat documentation/incident-response-playbook.md
```

---

## 🔍 Understanding the Attack Scenarios

### Attack 1: Price Manipulation (attacker_001)
```
View: $299.99 → Intercept: $0.01 → Checkout: $0.05 total
Detector: ✅ CRITICAL alert - "PRICE_MANIPULATION"
Action: Block account, reverse $1,499.95 loss
```

### Attack 2: Negative Quantity (attacker_002)
```
Adds -10 items to cart → Charges -$750 (system owes attacker)
Detector: ✅ CRITICAL alert - "NEGATIVE_QUANTITY" + "NEGATIVE_PRICE"
Action: Block account, reverse $750 refund
```

### Attack 3: Discount Code Abuse (attacker_003)
```
Buys 100 items with 99% discount → Pays $129.50 instead of $12,950
Detector: ✅ HIGH alert - "EXTREME_DISCOUNT" (>80% threshold)
Action: Block account, reverse discount, investigate code leak
```

### Attack 4: Negative Price Injection (attacker_004)
```
Modifies price to -$99.99 per item (50 items) → System refunds $4,999.50
Detector: ✅ CRITICAL alert - "NEGATIVE_PRICE" (×2)
Action: Block account, reverse charges
```

### Attack 5: Quantity-Price Mismatch (attacker_005)
```
Orders 500 items → Pays for 1 item ($49.99 instead of $24,995)
Detector: ✅ CRITICAL alert - "QUANTITY_PRICE_MISMATCH"
Action: Block account, reverse charges, audit inventory
```

---

## 📊 Detection Rules at a Glance

| # | Rule | Trigger | Severity | False Pos. |
|---|---|---|---|---|
| 1 | Negative Quantity | qty < 0 | CRITICAL | Very Low |
| 2 | Negative Price | price < 0 | CRITICAL | Very Low |
| 3 | Price Manipulation | variance > 10% | CRITICAL | Medium |
| 4 | Qty-Price Mismatch | calc variance > 5% | CRITICAL | High |
| 5 | Extreme Discount | discount > 80% | HIGH | High |
| 6 | Total Mismatch | math error > 5% | HIGH | Medium |
| 7 | Anomaly Flags | RISK/ANOMALY in log | Variable | Low |

**All rules are implemented in `detector.py` and documented in `documentation/detection-rule.md`**

---

## 🚨 How to Use the Triage Checklist

**When an alert fires in production:**

1. **First 60 seconds:** Confirm it's real (check alert-triage-checklist.md Step 1-2)
2. **Next 2 minutes:** Assess severity and blast radius (Steps 3-4)
3. **Next 3 minutes:** Check for false positives (Steps 5-6)
4. **Decision:** Escalate to Incident Response or close as false positive

**Example workflow:**
```
ALERT: Negative price (-$750) from user_123
  ↓ Is this real? [Check logs] → YES
  ↓ Is this serious? [Calculate loss] → YES ($750 loss, CRITICAL)
  ↓ Is this a known false positive? [Check whitelist] → NO
  ↓ Are there red flags? [Check IP, account age] → YES (new account)
  ↓ DECISION: Escalate to Incident Response immediately
  ↓ Create ticket SEC-2024-BLFL-00X and notify team
```

See `documentation/alert-triage-checklist.md` for full template.

---

## 🔧 Incident Response Workflow

**When you CONFIRM an attack:**

### Phase 1: Detection & Alerting (0-15 min)
- ✅ Verify attack is real
- ✅ Create incident ticket
- ✅ Notify stakeholders

### Phase 2: Containment (15-45 min)
- ✅ Block attacker account
- ✅ Reverse fraudulent transactions
- ✅ Request code review from engineering
- ✅ Contact payment processor

### Phase 3: Investigation (30 min - 4 hours)
- ✅ Analyze attacker's activity (timeline, IP, behavior)
- ✅ Find all affected orders
- ✅ Determine root cause in code
- ✅ Calculate total financial impact

### Phase 4: Recovery & Communication (1-4 hours)
- ✅ Deploy security patch
- ✅ Notify affected customers
- ✅ Brief PR team if needed
- ✅ Close incident ticket with lessons learned

**Full playbook:** `documentation/incident-response-playbook.md`

---

## 🎓 Learning Objectives

By working through this lab, you'll understand:

### ✅ What You'll Learn
1. **Detection:** How to write log-based detection rules from scratch
2. **Triage:** How SOC analysts prioritize & validate alerts (tons of false positives!)
3. **Incident Response:** How to contain, investigate, and remediate attacks
4. **SIEM concepts:** Log parsing, correlation, alerting (without complex SIEM)
5. **Business logic:** How attackers exploit application flaws (not just network attacks)
6. **Playbook development:** How to document processes for your team

### ✅ Real Skills You'll Practice
- Reading and interpreting log data
- Writing detection queries/patterns
- Decision trees for alert assessment
- Incident communication & escalation
- Root cause analysis
- Post-incident documentation

### ✅ Real Mistakes to Avoid
- Writing rules so sensitive they generate 50+ false positives/day 🚫
- Assuming every alert is a real attack (alert fatigue is real) 🚫
- Not checking if legitimate activity looks "suspicious" 🚫
- Forgetting to notify stakeholders during incident response 🚫
- Deploying fixes without testing 🚫

---

## 📂 Folder Structure

```
Week4-SOC-Business-Logic/
│
├── logs/                          # Sample log files
│   ├── attack.log                 # 19 lines showing 5 attack scenarios
│   └── benign.log                 # 16 lines of normal traffic
│
├── documentation/                 # Playbooks & policies
│   ├── detection-rule.md          # 7 rules with CVSS scores, tuning guide
│   ├── alert-triage-checklist.md  # Step-by-step analyst workflow
│   ├── incident-response-playbook.md # Containment & remediation guide
│   └── limitations.md             # 9 documented blind spots + roadmap
│
├── testing/                       # Validation & results
│   ├── test-results.md            # Proof rules work, false positive analysis
│   ├── benign_results.txt         # Output from detector on clean logs
│   └── attack_results.txt         # Output from detector on attack logs
│
├── detector.py                    # Python detection engine (main tool)
│   └── [7 detection rules + log parser + alert formatter]
│
└── README.md                      # This file
```

---

## 🖥️ Running in VS Code

### Step 1: Open Folder
```bash
code Week4-SOC-Business-Logic
```

### Step 2: Open Terminal
```
View → Terminal (Ctrl+`)
```

### Step 3: Run Detector
```bash
python3 detector.py logs/benign.log
python3 detector.py logs/attack.log
```

### Step 4: View Output
- Colored alerts appear in terminal (red for CRITICAL, yellow for HIGH)
- JSON results saved to `detection_output.json`

### Step 5: Read Documentation
- Open `documentation/` folder
- Read files in order: detection-rule.md → alert-triage-checklist.md → incident-response-playbook.md

---

## 🧪 What to Try Next (After Completing the Lab)

### 1. **Add Your Own Logs**
Modify `logs/benign.log` and `logs/attack.log` with:
- New products/prices
- Your own discount codes
- Different user IDs
- Custom timestamps

Run detector again:
```bash
python3 detector.py logs/benign.log
```

### 2. **Modify Detection Rules**
Edit `detector.py` to:
- Change discount threshold from 80% → 75%
- Add a new rule for "bulk orders" (qty > 1000)
- Adjust price mismatch variance from 10% → 5%

Re-test against logs:
```bash
python3 detector.py logs/attack.log
```

### 3. **Practice Triage**
Simulate receiving alerts:
1. Read first alert from attack_results.txt
2. Follow `documentation/alert-triage-checklist.md` for 5 minutes
3. Make a decision: Escalate or close?
4. Compare your decision to documented response

### 4. **Run Incident Playbook**
Simulate incident response:
1. Pretend Alert #4 (negative price) just fired
2. Follow `documentation/incident-response-playbook.md` step-by-step
3. Document each action (block, reverse, notify, etc.)
4. Write a mock incident closure report

### 5. **Build Your Own Detector**
Create a detector for a different attack type:
- SQL injection in search logs
- Privilege escalation attempts
- Data exfiltration patterns
- API abuse (rate limiting violation)

Use `detector.py` as a template!

---

## 📞 Troubleshooting

### Issue: "Python3 not found"
```bash
# Check python version
python --version
# If it's Python 3.x, use:
python detector.py logs/benign.log
```

### Issue: "ModuleNotFoundError"
The detector uses only built-in Python libraries (no pip install needed).  
If you get an error, something might be corrupted:
```bash
# Verify detector.py is not empty
cat detector.py | head -20
```

### Issue: "detector.py: No such file or directory"
Make sure you're in the right directory:
```bash
cd Week4-SOC-Business-Logic
pwd  # Should show: .../Week4-SOC-Business-Logic
ls   # Should show: logs/ documentation/ testing/ detector.py README.md
```

### Issue: "No alerts detected when expecting alerts"
Check that you're running against `logs/attack.log`, not `logs/benign.log`:
```bash
# This should produce NO alerts:
python3 detector.py logs/benign.log

# This SHOULD produce 10 alerts:
python3 detector.py logs/attack.log
```

---

## 📖 Recommended Reading Order

**Total time: 1 hour**

| # | Document | Time | Purpose |
|---|---|---|---|
| 1 | This README | 10 min | **Orientation** — understand the big picture |
| 2 | detection-rule.md | 15 min | **Learn** — what attacks we catch & why |
| 3 | Alert output from `attack_results.txt` | 5 min | **See** — what real alerts look like |
| 4. | alert-triage-checklist.md | 15 min | **Practice** — how to analyze alerts |
| 5 | incident-response-playbook.md | 15 min | **Execute** — what to do when confirmed |

After 1 hour, you'll understand the complete SOC workflow for Business Logic Flaw attacks.

---

## ⭐ Key Takeaways

### What Business Logic Flaws Are
Attacks that exploit the BUSINESS RULES of an application (not network/OS flaws):
- Buying items for wrong price
- Ordering many items but paying for few
- Applying discounts incorrectly
- Manipulating quantity/total calculations
- Abusing refund logic

### Why They're Dangerous
- Often MISSED by traditional security tools (they look for malware, not logic errors)
- ANYONE can potentially exploit them (no special hacking tools needed)
- Can cause MASSIVE financial loss ($1000s-$100,000s per attack)
- Hard to trace (legitimate-looking requests, no network signatures)

### How to Defend Against Them
1. **Prevent** (best): Secure code (re-fetch prices from DB, validate all inputs)
2. **Detect** (this lab): Alert on suspicious patterns (what we built)
3. **Respond** (playbook): Contain & investigate quickly (documented)
4. **Learn** (continuous): Update rules based on new attacks (roadmap in limitations.md)

---

## 📊 Assignment Rubric (Self-Check)

### Have you completed all deliverables?
- [ ] Detection rule with documentation (`detection-rule.md`)
- [ ] Alert-triage checklist (`alert-triage-checklist.md`)
- [ ] Incident-response playbook (`incident-response-playbook.md`)
- [ ] Test results showing rule works (`testing/test-results.md`)
- [ ] Detector script (`detector.py`)
- [ ] Sample logs (both attack and benign) (`logs/benign.log`, `logs/attack.log`)
- [ ] Limitations documented (`limitations.md`)
- [ ] README (this file)

### Do your detection rules work?
- [ ] Zero false positives on benign logs
- [ ] 100% catch rate on attack logs
- [ ] Rules tested in production-like environment

### Is your documentation actionable?
- [ ] A SOC analyst could follow your playbooks without asking questions
- [ ] All steps are concrete (not vague)
- [ ] Examples included for each scenario
- [ ] Clear decision trees for escalation

### Can you explain it all?
- [ ] What business logic flaws are
- [ ] Why each detection rule exists
- [ ] How triage workflow reduces false positives
- [ ] What to do when an attack is confirmed
- [ ] What blind spots remain

---

## 🔗 External Resources

### Learning Resources
- [OWASP: Business Logic Flaws](https://owasp.org/www-community/attacks/Business_logic)
- [CWE-841: Improper Enforcement of Behavioral Workflow](https://cwe.mitre.org/data/definitions/841.html)
- [PCI DSS Requirement 6.5.10: Business Logic Flaws](https://www.pcisecuritystandards.org/)
- [YouTube: SOC Analyst Tutorial](https://www.youtube.com/results?search_query=SOC+analyst+tutorial)

### Test Your Vulnerability Understanding
- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) — Vulnerable app with business logic flaws
- [DVWA](https://dvwa.co.uk/) — Damn Vulnerable Web Application
- [HackTheBox](https://www.hackthebox.com/) — Security challenges

### Further Reading (After This Lab)
- Advanced SOC: Machine Learning for Anomaly Detection
- Cross-system Correlation (SIEM-level analysis)
- Threat Hunting: Finding attacks before alerts fire
- Purple Teaming: Red team attacks + Blue team defenses

---

## 💬 Questions?

### Common Questions

**Q: Why don't we just use Wazuh/Splunk?**  
A: This lab teaches SOC CONCEPTS without infrastructure overhead. Real SIEM tools are more complex; this gives you fundamentals.

**Q: Can I use this in production?**  
A: **Not yet.** This lab is for LEARNING. Production requirements: real SIEM, ML baselines, cross-system integration, 24/7 SOC team.

**Q: What if I find a flaw in the detector?**  
A: Great! Fix it and test your fix. That's exactly how real security works.

**Q: How long should this take?**  
A: 1-2 hours for complete understanding. 30 minutes if you just want to run the detector.

**Q: Can I extend this for a school project?**  
A: YES! Add: ML detection, more attack scenarios, cross-system correlation, API integration.

---

## 📝 License & Attribution

**This lab was created for educational purposes.**

- Based on real SOC workflows
- Detection rules inspired by OWASP, CWE, PCI DSS
- Sample attacks based on public research
- Free to use, modify, and share for learning

---

## 🎯 Final Checkpoint

**You're ready to move forward when you can answer:**

1. ✅ What is a Business Logic Flaw attack?
2. ✅ What are the 7 detection rules and when they trigger?
3. ✅ How do you triage an alert in <5 minutes?
4. ✅ What's the first thing you do when an attack is confirmed?
5. ✅ What are the known blind spots in this detection system?

If yes to all 5 → **You've completed Week 4!** 🎉

---

**Good luck, and remember: SOC work is about seeing the whole picture. One alert doesn't mean anything; patterns mean everything.**

---

**Last Updated:** 2024-09-16  
**Version:** 1.0 (Lab Ready)  
**Status:** ✅ PRODUCTION LEARNING ENVIRONMENT
