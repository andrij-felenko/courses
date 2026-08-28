PCT_DRY = 30                     # сухіше за 30 % → вмикаємо полив
PCT_WET = 60                     # вологіше за 60 % → вимикаємо
watering = False                 # поточний стан насоса

def decide(pct):                 # pct — уже згладжений відсоток вологості
    global watering
    if not watering and pct < PCT_DRY:  # пересохло → лий
        watering = True
    if watering and pct > PCT_WET:      # напоїлось → стоп
        watering = False
    # між 30 % і 60 % стан НЕ міняється — оце й є зона спокою
