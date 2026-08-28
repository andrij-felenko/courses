# Викликається періодично, поки список неповний:
def param_download_tick(self) -> None:
    if self.total == 0:                           # ще не почали
        return
    if self.have >= self.total:
        self.on_download_done()
        return
    if now_ms() - self.last_rx_ms < PARAM_TIMEOUT_MS:  # ще йдуть
        return

    # потік завмер, але маємо не все — перепитуємо діри по одній
    for i in range(self.total):
        if not self.got[i]:
            send_param_request_read(index=i)
    self.last_rx_ms = now_ms()                    # дамо їм час відповісти
