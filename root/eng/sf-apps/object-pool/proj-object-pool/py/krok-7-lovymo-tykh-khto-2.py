def release(self, conn):
    with self._cond:
        if conn not in self._in_use:         # ← тавро: цей об'єкт справді в оренді?
            raise ValueError(
                "повертають об'єкт, якого пул не видавав "
                "(подвійний release або чужий об'єкт)")
        self._in_use.discard(conn)           # знімаємо тавро оренди
    conn.reset()                             # чистимо ПОЗА замком (крок 4)
    with self._cond:
        self._free.append(conn)
        self._cond.notify()
