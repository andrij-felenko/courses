import math

# Прилад і схема
Vbus = 540.0      # В    силова шина
Vcc = 12.0        # В    плаваюче живлення VB − VS
Vth = 2.0         # В    поріг приймача, відлічений униз від VB
Cp = 1e-12        # Ф    паразитна ємність вузла SET/RESET
R = 3e3           # Ом   підтяжка
I = 2e-3          # А    струм іскри
dVdt = 50e9       # В/с  найкрутіший фронт вузла SW
fsw = 100e3       # Гц   частота перемикання
Dmin = 0.10       # —    найкоротша шпаруватість ШІМ
Pbudget = 50e-3   # Вт   скільки згодні спалити на зсуві рівня

k = I * R / Vth                              # запас спаду над порогом
tau = R * Cp

t_front = Vbus / dVdt                        # скільки триває стрибок домену
t_filter = 2 * t_front                       # фільтр мусить пересидіти стрибок
lo_detect = tau * math.log(k / (k - 1))      # встигнути перетнути поріг
lo_blank = 2 * t_filter                      # іскра мусить пережити фільтр
hi_power = Pbudget / (2 * fsw * Vbus * I)    # не спалити тепловий бюджет
hi_pwm = Dmin / fsw                          # влізти в найкоротший імпульс ШІМ

lo, hi = max(lo_detect, lo_blank), min(hi_power, hi_pwm)

print("запас k         = %.1f   (стеля k = Vcc/Vth = %.1f)" % (k, Vcc / Vth))
print("підлога: вияв   = %6.2f нс" % (lo_detect * 1e9))
print("підлога: фільтр = %6.2f нс" % (lo_blank * 1e9))
print("стеля:   тепло  = %6.1f нс" % (hi_power * 1e9))
print("стеля:   ШІМ    = %6.1f нс" % (hi_pwm * 1e9))
if lo < hi:
    print("вікно tp        = %.0f … %.0f нс  →  брати %.0f нс"
          % (lo * 1e9, hi * 1e9, math.sqrt(lo * hi) * 1e9))
else:
    print("вікна НЕМА: приладу з такими числами не існує")
