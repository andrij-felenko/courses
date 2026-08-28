# Стани ініціалізації SD по SPI — прямо з графа.
ST_POWER  = 0   # щойно ввімкнули: чекаємо стабілізації живлення
ST_WARMUP = 1   # ≥ 74 такти при CS=1
ST_IDLE   = 2   # після CMD0: картка в спокої, у SPI-режимі
ST_IFCOND = 3   # CMD8: звірка вольтажу й версії
ST_POLL   = 4   # ACMD41 у циклі, доки картка не звільниться
ST_READY  = 5   # CMD58 прочитано: готова, тип відомий
ST_ERROR  = 6   # глухий кут: мовчить або таймаут

class SdFsm:                     # m.hc: 1 якщо SDHC
    def __init__(self, spi, cs):
        self.spi, self.cs = spi, cs
        self.state, self.hc, self.tries = ST_POWER, 0, 0

# Один крок автомата: виконати дію поточного стану й повернути наступний стан.
# (sd_cmd — послати 6-байтову команду і дочекатися R1; визначена деінде.)
def sd_step(m):
    if m.state == ST_POWER:
        time.sleep_ms(2)                     # ≥ 1 мс після появи напруги
        return ST_WARMUP

    if m.state == ST_WARMUP:
        m.spi.init(baudrate=400_000)         # 100–400 кГц на весь час ініціалізації
        m.cs.value(1)
        for _ in range(10):                  # ≥ 74 такти, CS високий
            m.spi.read(1, 0xFF)
        return ST_IDLE

    if m.state == ST_IDLE:
        m.cs.value(0)
        if sd_cmd(m, 0, 0, 0x94) != 0x01:    # CMD0: чекаємо рівно 0x01 (idle)
            return ST_ERROR                  # мовчить/не той стан -> глухий кут
        return ST_IFCOND

    if m.state == ST_IFCOND:
        # CMD8: сучасна картка луною поверне 0x1AA у 4-байтовому «хвості» R7.
        # «Недозволена» (біт 0x04) означає стару картку — теж прямуємо в POLL.
        sd_cmd(m, 8, 0x000001AA, 0x86)
        for _ in range(4):                   # забрати хвіст R7
            m.spi.read(1, 0xFF)
        m.tries = 0
        return ST_POLL

    if m.state == ST_POLL:
        sd_cmd(m, 55, 0, 0xFF)               # CMD55: далі прикладна
        if sd_cmd(m, 41, 0x40000000, 0xFF) == 0x00:   # ACMD41, HCS=1
            return ST_READY                  # 0x00 -> картка готова
        m.tries += 1
        if m.tries > 1000:                   # таймаут циклу опитування
            return ST_ERROR
        return ST_POLL                       # ще busy -> самопетля

    if m.state == ST_READY:
        sd_cmd(m, 58, 0, 0xFF)               # CMD58: читаємо OCR
        ocr = m.spi.read(4, 0xFF)
        m.hc = 1 if (ocr[0] & 0x40) else 0   # біт CCS -> SDHC?
        m.cs.value(1)
        m.spi.init(baudrate=25_000_000)      # готово -> повна частота
        return ST_READY

    m.cs.value(1)                            # ST_ERROR
    return ST_ERROR

# Прокрутити автомат до READY або ERROR. Повертає 0, якщо картка готова.
def sd_init_fsm(m):
    m.state, m.hc, m.tries = ST_POWER, 0, 0
    while m.state != ST_READY and m.state != ST_ERROR:
        m.state = sd_step(m)
    # ще один крок у READY зчитує OCR і піднімає частоту
    if m.state == ST_READY:
        sd_step(m)
        return 0
    return -1                                # ST_ERROR
