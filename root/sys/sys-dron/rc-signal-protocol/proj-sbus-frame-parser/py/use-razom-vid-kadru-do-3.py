sb = SbusData()

result = sbus_read(sb)
if result is not None:
    sb, ch_us = result
    if sb.failsafe:
        enter_failsafe()               # утримати/повернутись/заглушити — за політикою апарата
    else:
        apply_throttle(ch_us[2])       # напр., газ на 3-му каналі, вже в мкс
        # frame_lost можна врахувати як «підозрілий кадр», але не як тривогу
