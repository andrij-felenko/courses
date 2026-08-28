# stop-and-wait ARQ: шлю критичну команду, поки не прийде ACK
# ACK_TIMEOUT — скільки чекати підтвердження; MAX_TRIES — стеля повторів
def send_reliable(seq, cmd):
    for _ in range(MAX_TRIES):
        send_packet(seq, cmd)                 # 1) передаю (чи повторно передаю)
        t0 = millis()
        while millis() - t0 < ACK_TIMEOUT:    # 2) чекаю ACK з цим же номером
            if got_ack_for(seq):
                return True                   #    дійшло й підтверджено
        # 3) тиша до таймауту → повтор тієї самої команди з тим самим seq
    return False                              # 4) MAX_TRIES марно → зв'язок мертвий

# ACK_TIMEOUT = 200 мс, MAX_TRIES = 5:
#   спроба 1 @ 0 мс    → тиша 200 мс
#   спроба 2 @ 200 мс  → тиша 200 мс
#   спроба 3 @ 400 мс  → тиша 200 мс
#   спроба 4 @ 600 мс  → тиша 200 мс
#   спроба 5 @ 800 мс  → тиша 200 мс
#   1000 мс: 5 спроб марно → return False → failsafe()
