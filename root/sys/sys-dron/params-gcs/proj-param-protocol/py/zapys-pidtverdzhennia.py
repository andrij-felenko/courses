SET_TIMEOUT_MS = 1000
SET_RETRIES    = 3

def param_set_blocking(id: bytes, want: float, type: int) -> bool:
    for _ in range(SET_RETRIES):
        send_param_set(id, want, type)
        t0 = now_ms()
        while now_ms() - t0 < SET_TIMEOUT_MS:
            pv = recv_param_value()
            if pv is not None and name_eq(pv.param_id, id):
                return float_eq(pv.param_value, want)   # борт підтвердив САМЕ це
        # тиша → пакет загубився, шлемо PARAM_SET ще раз
    return False   # борт так і не підтвердив — не вважаємо записаним
