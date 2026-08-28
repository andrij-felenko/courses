# Гістерезис brownout: падаємо низько, а вмикаємось назад із запасом,
# щоб не «дзеленчати» на межі (це саме те дрижання «раз із трьох»).
BROWNOUT_TRIP_MV  = 4000   # нижче цього — переходимо в економний режим
BROWNOUT_CLEAR_MV = 4300   # назад у повний режим лише вище цього (запас 300 мВ)

class PowerSupervisor:
    def __init__(self):
        self.low_power_mode = False   # стан живе в об'єкті, а не у file-scope static

    def supervise(self, vbus_mv: int) -> None:
        if not self.low_power_mode and vbus_mv < BROWNOUT_TRIP_MV:
            self.low_power_mode = True    # просіли — стишуємо апетит, а не падаємо
            reduce_load()                 # прибрати некритичне: підсвітку, радіо, тактову
        elif self.low_power_mode and vbus_mv > BROWNOUT_CLEAR_MV:
            self.low_power_mode = False   # напруга повернулась із запасом — знову повний режим
            restore_load()
        # проміжок 4000..4300 — «мертва зона» гістерезису: нічого не міняємо,
        # саме вона й не дає системі дрижати на самій межі порога
