import time
import sys
import requests
from typing import Dict, Any

class CanaryOrchestrator:
    """Оркестратор канареєчного розгортання для бекенду Digital Homes."""

    def __init__(self, prometheus_url: str, gateway_admin_url: str):
        self.prometheus_url = prometheus_url
        self.gateway_admin_url = gateway_admin_url
        self.session = requests.Session()

    def query_scalar_metric(self, promql: str) -> float:
        """Виконує PromQL запит та повертає скалярне значення метрики.
        
        У разі відсутності даних або помилки мережі повертає 0.0.
        """
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": promql},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            result = data.get("data", {}).get("result", [])
            if not result or "value" not in result[0]:
                return 0.0
            return float(result[0]["value"][1])
        except Exception as e:
            print(f"[WARN] Помилка виконання PromQL запиту '{promql}': {e}", file=sys.stderr)
            return 0.0

    def set_canary_weight(self, weight_percent: int) -> None:
        """Оновлює вагові коефіцієнти вхідного шлюзу Envoy.
        
        Розподіляє 100% трафіку між dh-backend-baseline та dh-backend-canary.
        """
        baseline_weight = 100 - weight_percent
        payload = {
            "routes": [
                {"cluster": "dh-backend-baseline", "weight": baseline_weight},
                {"cluster": "dh-backend-canary", "weight": weight_percent}
            ]
        }
        try:
            resp = self.session.post(
                f"{self.gateway_admin_url}/v1/routes/weight",
                json=payload,
                timeout=3.0
            )
            resp.raise_for_status()
            print(f"[ROUTER] Вагу трафіку оновлено: База={baseline_weight}%, Канарка={weight_percent}%")
        except Exception as e:
            print(f"[CRITICAL] Не вдалося оновити вагу трафіку в Envoy: {e}", file=sys.stderr)
            raise

    def evaluate_canary_health(self, step_duration_sec: int = 300) -> float:
        """Очікує час витримки та обчислює підсумкову оцінку здоров'я канарки."""
        print(f"[SOAK] Очікуємо час витримки (soak time): {step_duration_sec} секунд...")
        time.sleep(step_duration_sec)

        # 1. Відсоток помилок 5xx
        err_baseline = self.query_scalar_metric(
            'sum(rate(http_requests_total{job="dh-backend",version="v1.4",status=~"5.."}[5m])) '
            '/ (sum(rate(http_requests_total{job="dh-backend",version="v1.4"}[5m])) + 0.001)'
        )
        err_canary = self.query_scalar_metric(
            'sum(rate(http_requests_total{job="dh-backend",version="v1.5",status=~"5.."}[5m])) '
            '/ (sum(rate(http_requests_total{job="dh-backend",version="v1.5"}[5m])) + 0.001)'
        )

        # 2. Затримка 95-го перцентиля (p95 latency)
        p95_baseline = self.query_scalar_metric(
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="dh-backend",version="v1.4"}[5m])) by (le))'
        )
        p95_canary = self.query_scalar_metric(
            'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="dh-backend",version="v1.5"}[5m])) by (le))'
        )

        # 3. Частота перепідключень IoT-хабів
        reconn_baseline = self.query_scalar_metric('sum(rate(dh_device_reconnects_total{version="v1.4"}[5m]))')
        reconn_canary = self.query_scalar_metric('sum(rate(dh_device_reconnects_total{version="v1.5"}[5m]))')

        score = 100.0
        err_diff = err_canary - err_baseline

        print(f"[METRICS] Помилки: База={err_baseline:.4f}, Канарка={err_canary:.4f} (Δ={err_diff:.4f})")
        print(f"[METRICS] Затримка p95: База={p95_baseline:.3f}s, Канарка={p95_canary:.3f}s")
        print(f"[METRICS] Перепідключення: База={reconn_baseline:.2f}/s, Канарка={reconn_canary:.2f}/s")

        # Штраф за зростання помилок
        if err_diff > 0.005:
            print(f"[PENALTY] Зростання помилок на {err_diff*100:.2f}%! (-50 балів)")
            score -= 50.0

        # Штраф за деградацію затримки p95
        if p95_baseline > 0 and (p95_canary / p95_baseline) > 1.20:
            ratio = p95_canary / p95_baseline
            print(f"[PENALTY] Сповільнення p95 у {ratio:.2f} разів! (-30 балів)")
            score -= 30.0

        # Штраф за аномалію перепідключень хабів
        if reconn_baseline > 0 and (reconn_canary / reconn_baseline) > 1.50:
            ratio = reconn_canary / reconn_baseline
            print(f"[PENALTY] Спричинено шторм підключень хабів у {ratio:.2f} разів! (-40 балів)")
            score -= 40.0

        return max(0.0, score)

    def execute_progressive_rollout(self) -> bool:
        """Послідовний конвеєр розгортання: 1% -> 10% -> 50% -> 100%."""
        steps = [1, 10, 50, 100]
        for weight in steps:
            print(f"\n==========================================")
            print(f"[CANARY STEP] Початок фази: {weight}% трафіку")
            print(f"==========================================")
            
            self.set_canary_weight(weight)
            
            if weight == 100:
                print("[SUCCESS] Канарка успішно пройшла всі перевірки й стала базовою версією!")
                return True

            score = self.evaluate_canary_health(step_duration_sec=300)
            print(f"[EVALUATION] Підсумкова оцінка здоров'я: {score:.1f} / 100.0")

            if score < 75.0:
                print(f"[CRITICAL] Оцінка {score:.1f} нижча за поріг 75.0! Ініціація відкату!")
                self.rollback()
                return False

        return True

    def rollback(self) -> None:
        """Аварійне зняття трафіку з канарки та відновлення стабільного стану."""
        print("\n[ROLLBACK] Скидаємо трафік канарки в 0%! Усі запити ідуть на v1.4")
        try:
            self.set_canary_weight(0)
            print("[ROLLBACK] Відкат трафіку завершено успішно.")
        except Exception as e:
            print(f"[EMERGENCY] Не вдалося автоматично скинути трафік: {e}", file=sys.stderr)
