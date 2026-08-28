#!/usr/bin/env python3
"""Оцінка фітнес-функції вартості та формування вердикту для CI/CD."""

import json
import sys
import argparse
from typing import Dict, Any, List

# Корпоративні порогові значення за замовчуванням
MAX_ABSOLUTE_DIFF_USD = 200.0
MAX_RELATIVE_DIFF_PERCENT = 15.0
BYPASS_LABEL = "cost-bypass-approved"

def evaluate_guardrails(diff_data: Dict[str, Any], pr_event: Dict[str, Any]) -> Dict[str, Any]:
    """Аналіз JSON-звіту Infracost та генерація структурованого вердикту."""
    total_past = float(diff_data.get("totalPastMonthlyCost", "0") or "0")
    total_new = float(diff_data.get("totalMonthlyCost", "0") or "0")
    total_diff = float(diff_data.get("totalMonthlyCostDiff", "0") or "0")
    
    delta_percent = (total_diff / total_past * 100.0) if total_past > 0 else 0.0
    
    # Перевірка наявності мітки аварійного обходу у PR
    labels = [l["name"] for l in pr_event.get("pull_request", {}).get("labels", [])]
    has_bypass = BYPASS_LABEL in labels
    
    violations = []
    if total_diff > MAX_ABSOLUTE_DIFF_USD:
        violations.append(
            f"❌ Перевищено абсолютний поріг витрат: **+${total_diff:.2f}/міс** (ліміт: `${MAX_ABSOLUTE_DIFF_USD:.2f}/міс`)"
        )
    
    if delta_percent > MAX_RELATIVE_DIFF_PERCENT and total_past > 0:
        violations.append(
            f"❌ Перевищено відносний поріг витрат: **+{delta_percent:.1f}%** (ліміт: `${MAX_RELATIVE_DIFF_PERCENT:.1f}%`)"
        )
    
    # Визначення статусу
    status = "PASSED"
    status_emoji = "✅ PASSED"
    if violations:
        if has_bypass:
            status = "WARNING"
            status_emoji = "⚠️ WARNING (Bypassed)"
        else:
            status = "BLOCKED"
            status_emoji = "🚫 BLOCKED"
            
    # Побудова розгортки змін за ресурсами
    breakdown_items = []
    for project in diff_data.get("projects", []):
        for res in project.get("breakdown", {}).get("resources", []):
            diff = float(res.get("monthlyCostDiff", "0") or "0")
            if abs(diff) > 0.01:
                action = "➕" if diff > 0 else "➖"
                breakdown_items.append(f"| {action} `{res['name']}` | `{res['resourceType']}` | `${diff:+.2f}/міс` |")
                
    breakdown_md = "\n".join([
        "| Ресурс | Тип | Зміна витрат |",
        "| :--- | :--- | :--- |"
    ] + breakdown_items) if breakdown_items else "Змін у структурі витрат не виявлено."
    
    violations_md = "\n".join(violations) if violations else "Порушень фінансових лімітів не зафіксовано."
    if has_bypass and violations:
        violations_md += f"\n\n⚠️ **Примітка:** Блокування знято через наявність мітки `{BYPASS_LABEL}`."

    return {
        "status": status,
        "status_emoji": status_emoji,
        "past_monthly_cost": round(total_past, 2),
        "new_monthly_cost": round(total_new, 2),
        "delta_monthly_cost": round(total_diff, 2),
        "delta_percent": round(delta_percent, 1),
        "violations_markdown": violations_md,
        "breakdown_markdown": breakdown_md,
        "summary_reason": "; ".join(violations) if violations else "OK"
    }

def main():
    parser = argparse.ArgumentParser(description="FinOps Guardrail Evaluator")
    parser.add_argument("--diff-json", required=True, help="Шлях до JSON-файлу Infracost diff")
    parser.add_argument("--pr-event", required=True, help="Шлях до JSON-файлу події GitHub PR")
    parser.add_argument("--output-json", required=True, help="Шлях до вихідного результату")
    args = parser.parse_args()

    with open(args.diff_json, 'r', encoding='utf-8') as f:
        diff_data = json.load(f)
    with open(args.pr_event, 'r', encoding='utf-8') as f:
        pr_event = json.load(f)

    result = evaluate_guardrails(diff_data, pr_event)

    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
