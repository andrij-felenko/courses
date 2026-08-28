# power_diag.py (продовження) — ще один метод класу PwrDiagCtx

    # Чесне слово людині за ПРИЙНЯТИМ (стабільним) діагнозом.
    # Повертає короткий рядок; UI показує його замість німого блимання.
    def message(self) -> str:
        if not self.valid:
            return "Перевірка живлення..."     # ще не міряли під навантаженням

        if self.diag == PwrDiag.OK:
            return ("Живлення слабке: працюю ощадливо"   # тримаємось, але стишились
                    if self.low_power else
                    "Заряджання в нормі")
        if self.diag == PwrDiag.CABLE_DROP:
            return "Заряджаю повільно: схоже на кабель — спробуйте товщий або коротший"
        if self.diag == PwrDiag.NEGOTIATION:
            return "Обмежене живлення: цей кабель або блок не дає повного струму"
        if self.diag == PwrDiag.SOFT_SOURCE:
            return "Слабкий блок: напруга просідає під навантаженням — спробуйте інший"
        if self.diag == PwrDiag.NO_POWER:
            return "Живлення нема: перевірте кабель і почистіть роз'єм"
        return "Стан живлення невідомий"
