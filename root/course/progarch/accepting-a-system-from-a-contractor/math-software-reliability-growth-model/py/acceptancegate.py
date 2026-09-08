import sys
from typing import List

class AcceptanceGate:
    def __init__(self, target_mtbf_hours: float, max_residual_defects: float):
        self.target_mtbf = target_mtbf_hours
        self.max_residual = max_residual_defects

    def evaluate_release(self, failure_times: List[float]) -> bool:
        # Калібрування моделі Гоела-Окумото методом MLE
        from scratch.write_srgm_pismo_3_4 import GoelOkumotoMLE
        
        estimator = GoelOkumotoMLE(failure_times)
        try:
            a_opt, b_opt, residual = estimator.fit()
        except ValueError as err:
            print(f"[REJECT] Помилка калібрування моделі: {err}")
            return False

        t_n = failure_times[-1]
        current_intensity = a_opt * b_opt * (2.718281828459045 ** (-b_opt * t_n))
        current_mtbf = 1.0 / current_intensity if current_intensity > 0 else float("inf")

        print(f"--- Результати оцінки надійності SRGM ---")
        print(f"Загальний оцінений пул дефектів (a): {a_opt:.2f}")
        print(f"Темп виявлення (b): {b_opt:.5f} 1/год")
        print(f"Поточний MTBF: {current_mtbf:.2f} год (Цільовий: {self.target_mtbf:.2f} год)")
        print(f"Оцінка залишкових дефектів: {residual:.2f} (Ліміт: {self.max_residual:.2f})")

        # Перевірка контрактних критеріїв приймання
        passed_mtbf = current_mtbf >= self.target_mtbf
        passed_residual = residual <= self.max_residual

        if passed_mtbf and passed_residual:
            print("[ACCEPT] Система задовольняє вимогам надійності. Реліз схвалено.")
            return True
        else:
            print("[REJECT] Система не відповідає контрактним критеріям надійності:")
            if not passed_mtbf:
                print(f"  - MTBF {current_mtbf:.2f} год є нижчим за контрактний поріг {self.target_mtbf:.2f} год")
            if not passed_residual:
                print(f"  - Залишок дефектів {residual:.2f} перевищує ліміт {self.max_residual:.2f}")
            return False
