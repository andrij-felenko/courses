# ci_cost_guard.py — Скрипт перевірки фітнес-функції бюджету в CI
import sys
import yaml

def check_budget_policy(policy_file_path: str, max_allowed_unit_cost: float = 0.015) -> bool:
    with open(policy_file_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    fleet_size = spec.get("fleet_size", 5000000)
    sensors = spec.get("sensors", [])
    
    total_monthly_msgs = 0
    total_bytes = 0
    
    for s in sensors:
        freq_sec = s["interval_sec"]
        bytes_size = s["payload_bytes"]
        delta_ratio = s.get("delta_filter_ratio", 0.9)
        
        # 30 днів = 2592000 сек
        raw_msgs = (2592000 / freq_sec) * (1.0 - delta_ratio)
        total_monthly_msgs += raw_msgs * fleet_size
        total_bytes += raw_msgs * (bytes_size + 78) * fleet_size

    total_storage_gb = total_bytes / (1024 ** 3)
    
    # EMQX amortized + S3 Cold Storage
    cost_broker = (total_monthly_msgs / 1_000_000) * 0.05
    cost_storage = total_storage_gb * 0.015
    
    total_cost = cost_broker + cost_storage
    unit_cost = total_cost / fleet_size

    print(f"=== DH ARCHITECTURE FITNESS FUNCTION ===")
    print(f"Флот: {fleet_size:,} будинків")
    print(f"Прогнозовані хмарні витрати: ${total_cost:,.2f} / місяць")
    print(f"Unit Cost: ${unit_cost:.4f} / дім / місяць (Ліміт: ${max_allowed_unit_cost:.3f})")

    if unit_cost > max_allowed_unit_cost:
        print(f"❌ REJECTED: Бюджетний поріг перевищено на {((unit_cost/max_allowed_unit_cost)-1)*100:.1f}%!")
        return False
    
    print(f"✅ PASSED: Зміна не порушує фінансових обмежень.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci_cost_guard.py <telemetry_policy.yaml>")
        sys.exit(2)
        
    passed = check_budget_policy(sys.argv[1])
    sys.exit(0 if passed else 1)
