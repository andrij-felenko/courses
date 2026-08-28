import random

SLOT_US = 9       # тривалість одного "слота" тиші, мкс
DIFS_US = 34      # канал має бути вільним стільки перед стартом
CW_MIN  = 15      # початковий діапазон відступу (слотів)
CW_MAX  = 1023    # стеля діапазону

# channel_busy(), micros(), delay_us(), radio_transmit(), wait_for_ack()
# — апаратні примітиви радіочипа

def wait_idle_for(gap_us):
    """Чекати, доки канал не буде вільним суцільно gap_us мікросекунд."""
    while True:
        while channel_busy():        # зайнято — чекаємо звільнення
            pass
        t0 = micros()
        while not channel_busy():
            if micros() - t0 >= gap_us:
                return               # витримали всю тишу
        # хтось заговорив посеред паузи — починаємо відлік тиші наново

def csma_send(frame):
    """Одна спроба надіслати кадр; повертає True, якщо прийшов ACK."""
    cw = CW_MIN

    for _ in range(7):
        wait_idle_for(DIFS_US)              # 1. канал вільний DIFS?

        # 2. випадковий відступ у слотах із поточного діапазону
        backoff = random.randint(0, cw)
        while backoff > 0:
            if channel_busy():              #   хтось зайняв ефір —
                wait_idle_for(DIFS_US)      #   заморозити лічильник,
                continue                    #   доерахувати після тиші
            delay_us(SLOT_US)
            backoff -= 1                    #   тихий слот — крок вниз

        radio_transmit(frame)               # 3. лічильник 0 → передаємо
        if wait_for_ack():                  # 4. дочекалися ACK?
            return True                     #    доставлено

        cw = cw * 2 + 1                     # 5. зіткнення: подвоїти діапазон
        if cw > CW_MAX:
            cw = CW_MAX

    return False                            # здалися після кількох спроб
