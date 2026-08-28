from contextlib import contextmanager

class SqlTransactionManager:
    def __init__(self, pool):
        self._pool = pool

    @contextmanager
    def begin(self):
        conn = self._pool.connect()
        conn.execute("BEGIN")
        try:
            yield conn                   # усі кроки сценарію — у тілі with
            conn.execute("COMMIT")       # вийшли без винятку → закріпити
        except Exception:
            conn.execute("ROLLBACK")     # будь-який збій → відкотити все
            raise                        # і проштовхнути помилку далі
        finally:
            conn.close()                 # з'єднання завжди звільняється
