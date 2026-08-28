CYCLES   = 8             # скільки пар «увімк/вимк» накопичити
PHASE_US = 300           # тривалість півперіоду (встановлення + вимір)

# Синхронний детектор: сума «світлих» мінус сума «темних» фаз.
def read_sync():
    acc = 0
    for _ in range(CYCLES):
        led.value(1)                 # плюс-фаза
        time.sleep_us(PHASE_US)
        acc += adc.read()

        led.value(0)                 # мінус-фаза
        time.sleep_us(PHASE_US)
        acc -= adc.read()
    return acc                       # рівне тло зникло, відбиток × CYCLES

while True:
    signal = read_sync()
    obstacle = signal > 8 * 120      # поріг масштабується на CYCLES
    print("сигнал={}  перешкода={}".format(signal, int(obstacle)))
    time.sleep_ms(20)
