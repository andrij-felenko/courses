PERIOD = 4000                     # повний вдих-видих, мс
# gamma_lut — таблиця гамми з попереднього кроку (256 значень 0..65535)

while True:
    now = time.ticks_ms()
    phase = (now % PERIOD) / PERIOD                # 0..1, циклічно
    # синус робить плавний підйом і спад; зсуваємо в діапазон 0..1:
    bright = (1.0 - math.cos(phase * 2.0 * math.pi)) * 0.5   # 0→1→0
    level = int(bright * 255.0)
    led.duty_u16(gamma_lut[level])                 # гамма + вивід — як ми вже вміємо
    # цикл лишається вільним для всього іншого
