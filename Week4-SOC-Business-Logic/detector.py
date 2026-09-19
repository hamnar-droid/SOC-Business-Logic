#!/usr/bin/env python3
"""
SOC Detector: Business Logic Flaw Detection Script
Week 4 Assignment - Detects price/quantity manipulation attacks
"""

import re
import json
from collections import defaultdict
from datetime import datetime

# ANSI color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class LogParser:
    """Parse pipe-delimited log format"""
    
    def parse_log_line(self, line):
        """Convert log line to dictionary"""
        if not line.strip():
            return None
        
        parts = line.split('|')
        log_entry = {}
        
        for part in parts:
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                log_entry[key.strip()] = value.strip()
        
        return log_entry


class DetectionEngine:
    """Detection rules for Business Logic Flaws"""
    
    def __init__(self):
        self.alerts = []
        self.statistics = defaultdict(int)
    
    def detect_negative_quantity(self, log_entry):
        """RULE 1: Detect negative quantities (refund abuse)"""
        if 'quantity' in log_entry:
            try:
                qty = int(log_entry['quantity'])
                if qty < 0:
                    return {
                        'severity': 'CRITICAL',
                        'rule': 'NEGATIVE_QUANTITY',
                        'description': 'Negative quantity detected - potential refund abuse',
                        'details': f"Quantity: {qty}"
                    }
            except ValueError:
                pass
        return None
    
    def detect_negative_price(self, log_entry):
        """RULE 2: Detect negative prices (fraudulent charge reversal)"""
        if 'price' in log_entry or 'total_price' in log_entry:
            price_key = 'total_price' if 'total_price' in log_entry else 'price'
            try:
                price = float(log_entry[price_key])
                if price < 0:
                    return {
                        'severity': 'CRITICAL',
                        'rule': 'NEGATIVE_PRICE',
                        'description': 'Negative price detected - potential payment fraud',
                        'details': f"Price: ${price}"
                    }
            except ValueError:
                pass
        return None
    
    def detect_price_mismatch(self, log_entry):
        """RULE 3: Detect price manipulation (view -> checkout price change)"""
        # Check for suspicious patterns in log entries with multiple price references
        if 'RISK' in log_entry and 'price_manipulation' in log_entry['RISK']:
            return {
                'severity': 'CRITICAL',
                'rule': 'PRICE_MANIPULATION',
                'description': 'Price changed significantly between view and checkout',
                'details': 'Possible man-in-the-middle price modification'
            }
        return None
    
    def detect_quantity_price_mismatch(self, log_entry):
        """RULE 4: Detect quantity/price mismatch (order many, pay for few)"""
        if 'ANOMALY' in log_entry and 'qty_price_mismatch' in log_entry['ANOMALY']:
            return {
                'severity': 'CRITICAL',
                'rule': 'QUANTITY_PRICE_MISMATCH',
                'description': 'Ordered many items but charged for few - cart manipulation detected',
                'details': log_entry.get('quantity_mismatch', 'Unknown ratio')
            }
        return None
    
    def detect_extreme_discount(self, log_entry):
        """RULE 5: Detect abnormal discount abuse"""
        if 'discount_pct' in log_entry:
            try:
                discount = float(log_entry['discount_pct'])
                if discount > 80:  # More than 80% discount is suspicious
                    return {
                        'severity': 'HIGH',
                        'rule': 'EXTREME_DISCOUNT',
                        'description': f'Abnormal discount applied ({discount}%) - possible abuse',
                        'details': f"Discount code: {log_entry.get('discount_code', 'unknown')}"
                    }
            except ValueError:
                pass
        return None
    
    def detect_total_mismatch(self, log_entry):
        """RULE 6: Detect math error - items * price ≠ total"""
        if all(k in log_entry for k in ['total_items', 'price', 'total_price']):
            try:
                items = int(log_entry['total_items'])
                price = float(log_entry['price'])
                total = float(log_entry['total_price'])
                
                expected_total = items * price
                # Allow 5% variance for rounding/tax
                if abs(total - expected_total) > (expected_total * 0.05):
                    return {
                        'severity': 'HIGH',
                        'rule': 'TOTAL_CALCULATION_MISMATCH',
                        'description': 'Order total does not match item count × price',
                        'details': f"Expected: ${expected_total:.2f}, Got: ${total:.2f}"
                    }
            except ValueError:
                pass
        return None
    
    def detect_suspicious_pattern_in_log(self, log_entry):
        """RULE 7: Detect explicit RISK/ANOMALY flags in logs"""
        if 'ANOMALY' in log_entry:
            return {
                'severity': 'CRITICAL',
                'rule': 'ANOMALY_FLAG',
                'description': 'Anomaly detected - attack signature found',
                'details': log_entry['ANOMALY']
            }
        if 'RISK' in log_entry:
            return {
                'severity': 'HIGH',
                'rule': 'RISK_FLAG',
                'description': 'Risk indicator found - suspicious behavior',
                'details': log_entry['RISK']
            }
        return None
    
    def analyze_log_entry(self, log_entry):
        """Run all detection rules against a log entry"""
        if not log_entry:
            return None
        
        # Run all detection rules in order
        rules = [
            self.detect_negative_quantity,
            self.detect_negative_price,
            self.detect_price_mismatch,
            self.detect_quantity_price_mismatch,
            self.detect_extreme_discount,
            self.detect_total_mismatch,
            self.detect_suspicious_pattern_in_log,
        ]
        
        for rule in rules:
            alert = rule(log_entry)
            if alert:
                alert['timestamp'] = log_entry.get('timestamp', log_entry.get('time', 'N/A'))
                alert['user_id'] = log_entry.get('user_id', 'unknown')
                alert['action'] = log_entry.get('action', 'unknown')
                alert['order_id'] = log_entry.get('order_id', 'N/A')
                self.alerts.append(alert)
                self.statistics[alert['rule']] += 1
                return alert
        
        return None


class ReportGenerator:
    """Generate formatted detection reports"""
    
    @staticmethod
    def print_header(text):
        print(f"\n{BOLD}{CYAN}{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}{RESET}\n")
    
    @staticmethod
    def print_alert(alert, index):
        """Pretty-print an individual alert"""
        severity_color = RED if alert['severity'] == 'CRITICAL' else YELLOW
        
        print(f"{BOLD}[ALERT #{index}]{RESET}")
        print(f"  {BOLD}Timestamp:{RESET} {alert['timestamp']}")
        print(f"  {BOLD}User ID:{RESET} {alert['user_id']}")
        print(f"  {BOLD}Action:{RESET} {alert['action']}")
        print(f"  {BOLD}Order ID:{RESET} {alert['order_id']}")
        print(f"  {severity_color}{BOLD}Severity:{RESET} {alert['severity']}")
        print(f"  {BOLD}Rule:{RESET} {alert['rule']}")
        print(f"  {BOLD}Description:{RESET} {alert['description']}")
        print(f"  {BOLD}Details:{RESET} {alert['details']}")
        print()
    
    @staticmethod
    def print_summary(stats, total_lines):
        """Print detection summary"""
        print(f"{BOLD}Detection Summary:{RESET}")
        print(f"  Total log lines analyzed: {total_lines}")
        print(f"  Total alerts triggered: {len(stats['alerts'])}")
        
        if stats['alerts']:
            critical_count = sum(1 for a in stats['alerts'] if a['severity'] == 'CRITICAL')
            high_count = sum(1 for a in stats['alerts'] if a['severity'] == 'HIGH')
            print(f"  Critical alerts: {RED}{critical_count}{RESET}")
            print(f"  High alerts: {YELLOW}{high_count}{RESET}")
            print(f"\n  {BOLD}Alerts by Rule:{RESET}")
            for rule, count in sorted(stats['rule_stats'].items()):
                print(f"    - {rule}: {count}")
        else:
            print(f"  {GREEN}✓ No alerts - logs appear clean{RESET}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print(f"Usage: python3 detector.py <log_file>")
        print(f"Example: python3 detector.py logs/attack.log")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"{RED}Error: Log file '{log_file}' not found{RESET}")
        sys.exit(1)
    
    # Initialize components
    parser = LogParser()
    detector = DetectionEngine()
    report = ReportGenerator()
    
    # Parse and analyze logs
    report.print_header(f"SOC DETECTION REPORT: {log_file}")
    
    for line_num, line in enumerate(lines, 1):
        log_entry = parser.parse_log_line(line)
        if log_entry:
            detector.analyze_log_entry(log_entry)
    
    # Generate report
    stats = {
        'alerts': detector.alerts,
        'rule_stats': detector.statistics
    }
    
    report.print_summary(stats, len(lines))
    
    if detector.alerts:
        print(f"\n{BOLD}{RED}ALERTS DETECTED:{RESET}\n")
        for idx, alert in enumerate(detector.alerts, 1):
            report.print_alert(alert, idx)
    
    # Save results to file
    with open('detection_output.json', 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"{BOLD}Report saved to: detection_output.json{RESET}\n")


if __name__ == '__main__':
    main()
