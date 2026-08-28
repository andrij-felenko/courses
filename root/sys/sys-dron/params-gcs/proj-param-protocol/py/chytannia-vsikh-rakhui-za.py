PARAM_TIMEOUT_MS = 1000     # тиша довша за це = потік завмер

class ParamDownload:
    def __init__(self):
        self.total = 0            # param_count з першого пакета
        self.have = 0             # скільки вже маємо
        self.names = []           # таблиця імен, розмір param_count
        self.values = []
        self.got = []             # got[i] — чи прийшов параметр i
        self.last_rx_ms = 0       # коли прийшов останній PARAM_VALUE

    # Викликається на КОЖЕН вхідний PARAM_VALUE:
    def on_param_value(self, p: ParamValue) -> None:
        if self.total == 0:                       # перший пакет задає розмір
            self.total  = p.param_count
            self.names  = [b""]    * self.total
            self.values = [0.0]    * self.total
            self.got    = [False]  * self.total
        i = p.param_index
        if i < self.total and not self.got[i]:    # дублікати ігноруємо
            self.names[i]  = p.param_id[:16]
            self.values[i] = p.param_value
            self.got[i]    = True
            self.have     += 1
        self.last_rx_ms = now_ms()                # потік живий — зсуваємо таймер
