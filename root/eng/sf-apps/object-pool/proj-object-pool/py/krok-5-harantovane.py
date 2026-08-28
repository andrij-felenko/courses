from contextlib import contextmanager

class Pool:
    # ... acquire / release, як у кроці 4 ...

    @contextmanager
    def lease(self):
        conn = self.acquire()          # вхід у with — позичили
        try:
            yield conn                 # віддали користувачеві на час блоку
        finally:
            self.release(conn)         # вихід із with — повернули, завжди

# використання: повернення НЕ можна забути — його робить сам with
def handle(pool):
    with pool.lease() as conn:         # ← позичив
        rows = conn.query("select ...")
        if not rows:
            return None                # release однаково станеться
        process(rows)
    # ← тут conn уже повернутий, хай яким шляхом вийшли з блоку
