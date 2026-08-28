def acquire(self):
    with self._cond:
        deadline = _now() + self._timeout
        while True:
            if self._free:
                conn = self._free.pop()
                if not conn.is_alive():      # ← протух на полиці?
                    self._created -= 1       # списуємо мертвий
                    continue                 # шукаємо/родимо інший
                self._in_use.add(conn)
                return conn                  # віддаємо лише живий
            # ... далі як у кроці 4: рости / чекати / таймаут ...
