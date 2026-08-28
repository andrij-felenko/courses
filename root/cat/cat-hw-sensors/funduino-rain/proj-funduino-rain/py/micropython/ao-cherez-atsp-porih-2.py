from machine import ADC, Pin
import time

ao = ADC(Pin(34))
ao.atten(ADC.ATTN_11DB)
DRY_ENTER = 800                     # вище цього вважаємо «сухо»
WET_ENTER = 500                     # нижче цього вважаємо «дощ»
#   ЗВЕРНІТЬ УВАГУ: DRY_ENTER > WET_ENTER — між ними «мертва зона» гістерезису

raining = False

while True:
    v = ao.read()                   # менше число = мокріше

    # двопороговий гістерезис прямо на числі:
    #   у «дощ» переходимо, лише впавши НИЖЧЕ WET_ENTER;
    #   у «сухо» — лише піднявшись ВИЩЕ DRY_ENTER.
    if not raining and v < WET_ENTER:
        raining = True
    if raining and v > DRY_ENTER:
        raining = False

    print("AO =", v, "  → дощ" if raining else "  → сухо")
    time.sleep_ms(200)
