DRY = 680                         # сухіше за це (більше число) → вмикаємо полив
WET = 430                         # вологіше за це (менше число) → вимикаємо
watering = False                  # поточний стан насоса

def decide(soil):                 # soil — уже згладжене медіаною число
    global watering
    if not watering and soil > DRY:   # пересохло → лий
        watering = True
    if watering and soil < WET:       # напоїлось → стоп
        watering = False
    # між WET і DRY стан НЕ міняється — оце й є зона спокою
