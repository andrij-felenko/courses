# controller.py — Python-реалізація контролера заморозки релізів
import os
import time
import requests
from kubernetes import client, config

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus-k8s.monitoring:9090")
SLO_TARGET = 0.999  # 99.9%
WINDOW_SECONDS = 30 * 24 * 3600  # 30 днів
CONFIGMAP_NAME = "dh-release-policy"
NAMESPACE = "dh-system"

def query_prometheus(query: str) -> float:
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=10)
    response.raise_for_status()
    data = response.json()
    result = data.get("data", {}).get("result", [])
    if not result:
        return 0.0
    return float(result[0]["value"][1])

def calculate_remaining_budget() -> float:
    # Запит кількості невдалих запитів за 30 днів
    query_errors = f'sum(increase(dh_http_server_request_duration_seconds_count{{job="dh-lock-service", http_status_code!="200"}}[{WINDOW_SECONDS}s]))'
    query_total = f'sum(increase(dh_http_server_request_duration_seconds_count{{job="dh-lock-service"}}[{WINDOW_SECONDS}s]))'
    
    total_requests = query_prometheus(query_total)
    if total_requests == 0:
        return 100.0  # Немає трафіку — бюджет повний
        
    error_requests = query_prometheus(query_errors)
    current_sli = (total_requests - error_requests) / total_requests
    allowed_errors = total_requests * (1.0 - SLO_TARGET)
    
    remaining_budget_percent = ((allowed_errors - error_requests) / allowed_errors) * 100.0
    print(f"SLI: {current_sli:.5f} | Total: {total_requests} | Errors: {error_requests} | Budget Remaining: {remaining_budget_percent:.2f}%")
    return remaining_budget_percent

def update_k8s_freeze_policy(freeze: bool):
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
        
    v1 = client.CoreV1Api()
    cm = v1.read_namespaced_config_map(name=CONFIGMAP_NAME, namespace=NAMESPACE)
    current_val = cm.data.get("RELEASE_FREEZE_ENABLED", "false")
    new_val = "true" if freeze else "false"
    
    if current_val != new_val:
        cm.data["RELEASE_FREEZE_ENABLED"] = new_val
        v1.patch_namespaced_config_map(name=CONFIGMAP_NAME, namespace=NAMESPACE, body=cm)
        print(f"ПОЛІТИКУ ЗМІНЕНО: RELEASE_FREEZE_ENABLED = {new_val}")

def main():
    while True:
        try:
            budget = calculate_remaining_budget()
            if budget <= 0.0:
                print("УВАГА: Бюджет помилок вичерпано! Активація Freeze Policy.")
                update_k8s_freeze_policy(freeze=True)
            else:
                update_k8s_freeze_policy(freeze=False)
        except Exception as e:
            print(f"Помилка виконання контролера: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()
