class Employee:
    def __init__(self, data: EmployeeData):
        self._data = data

    # CFO: зарплата = звичайні години × ставка
    #             + понаднормові × ставка × 1.5
    def calculate_pay(self) -> float:
        reg = self._regular_hours()                  # ← спільна арифметика
        overtime = self._total_hours() - reg
        return (reg * self._data.hourly_rate
                + overtime * self._data.hourly_rate * 1.5)

    # COO: рядок звіту — окремо звичайні, окремо понаднормові
    def report_hours(self) -> str:
        reg = self._regular_hours()                  # ← та сама спільна
        overtime = self._total_hours() - reg
        return f"{self._data.name}: reg={reg:g} ot={overtime:g}"

    def save(self) -> None:
        ...                              # пише self._data у базу — тут не суттєво

    def _total_hours(self) -> float:
        return sum(self._data.daily_hours)

    # ПРИХОВАНА СПІЛЬНА ЗАЛЕЖНІСТЬ ДВОХ АКТОРІВ.
    # Скільки годин рахувати як «звичайні» (решта — понаднормові).
    # Політика підприємства: не більше 40 звичайних годин за період.
    def _regular_hours(self) -> float:
        return min(self._total_hours(), 40.0)
