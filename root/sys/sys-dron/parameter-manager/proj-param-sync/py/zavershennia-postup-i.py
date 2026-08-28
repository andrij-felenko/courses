    def complete(self):
        # Порожні карти очікування — ще НЕ все: параметри підвіса можуть приїхати
        # першими, а головного компонента не бути взагалі.
        if any(self.waiting.values()):
            return False
        return self.default_comp in self.total

    def progress(self):
        total = sum(self.total.values())
        left  = sum(len(w) for w in self.waiting.values())
        return (total - left) / total if total else 0.0


def fetch(conn, target_sys, default_comp):
    f = ParamFetcher(conn, target_sys, default_comp)
    f.start()
    while not (f.complete() or f.give_up):
        m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.2)
        now = time.monotonic()
        if m is not None and m.get_srcSystem() == target_sys:
            f.on_param_value(m.get_srcComponent(), m, now)
        f.tick(now)          # 0.2 с без кадрів — таймери все одно треба крутити
    return f
