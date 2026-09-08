# scripts/check_contract_acceptance.py
import sys
import math

def verify_acceptance_gate(
    loc: int,
    n1: int,
    n2: int,
    m: int,
    theta_defect: float = 1.0
) -> bool:
    """
    Перевірка статистичного критерію приймання коду за Чепменом.
    loc: фактичний обсяг зміненого коду в LOC
    n1: кількість зауважень першого рецензента
    n2: кількість зауважень другого рецензента
    m: кількість спільних зауважень
    theta_defect: максимально допустима залишкова щільність (дефектів/kLOC)
    """
    print(f"--- АНАЛІЗ ПРИЙМАННЯ РОБІТ (Обсяг: {loc} LOC) ---")
    print(f"Знахідки: R1={n1}, R2={n2}, Спільні={m}")

    # Перевірка 1: Аномалія нульового перетину
    if n1 >= 5 and n2 >= 5 and m == 0:
        print("ВЕРДИКТ: ВІДХИЛЕНО. Аномалія нульового перетину (m=0 при значних n1, n2).")
        print("Простір дефектів некорельований і неосяжний. Код потребує повного рефакторингу.")
        return False

    # Обчислення оцінювача Чепмена
    chapman_total = ((n1 + 1) * (n2 + 1)) / (m + 1) - 1.0
    found_unique = n1 + n2 - m
    rem_defects = max(0.0, chapman_total - found_unique)
    
    # Розрахунок залишкової щільності на 1000 LOC
    rho_rem = (rem_defects / loc) * 1000.0

    # Дисперсія та похибка
    var_c = ((n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m)) / (((m + 1) ** 2) * (m + 2))
    se_c = math.sqrt(max(0.0, var_c))

    print(f"Оцінена повна кількість дефектів (Чепмен): {chapman_total:.2f}")
    print(f"Фактично виявлено унікальних дефектів: {found_unique}")
    print(f"Очікувана кількість невидимих дефектів N_rem: {rem_defects:.2f} (SE={se_c:.2f})")
    print(f"Залишкова щільність: {rho_rem:.2f} дефектів/kLOC (Поріг: {theta_defect:.2f})")

    # Перевірка 2: Поріг залишкової щільності
    if rho_rem > theta_defect:
        print(f"ВЕРДИКТ: ВІДХИЛЕНО. Залишкова щільність ({rho_rem:.2f}) перевищує контрактний ліміт ({theta_defect:.2f}).")
        print("Підрядник зобов'язаний надати додаткові тести та провести внутрішню ревізію.")
        return False

    print("ВЕРДИКТ: ПРИЙНЯТО. Залишкова щільність відповідає критеріям Definition of Done.")
    return True

if __name__ == "__main__":
    # Приклад запуску: python check_contract_acceptance.py 300 8 6 3 1.0
    loc_arg = int(sys.argv[1])
    n1_arg = int(sys.argv[2])
    n2_arg = int(sys.argv[3])
    m_arg = int(sys.argv[4])
    theta_arg = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0

    accepted = verify_acceptance_gate(loc_arg, n1_arg, n2_arg, m_arg, theta_arg)
    sys.exit(0 if accepted else 1)
