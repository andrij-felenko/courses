# Шлю критичну команду stop-and-wait. True — підтверджено, False — зв'язок мертвий.
def send_reliable(seq, cmd):
    for _ in range(MAX_TRIES):
        send_packet(seq, cmd)                  # 1) передаю (чи повторно — той самий seq)
        t0 = millis()
        while millis() - t0 < ACK_TIMEOUT:     # 2) чекаю ACK саме з цим номером
            if got_ack_for(seq):
                return True                    #    дійшло й підтверджено
        # 3) тиша до таймауту → наступна ітерація повторить той самий seq
    return False                               # 4) MAX_TRIES марно → обрив
