class Hold:
    """Утримання одного виходу: володіння починається на вході в блок with
    і закінчується на виході з нього — будь-якому, зокрема через виняток."""

    def __init__(self, link, function):
        self.link, self.function = link, function
        self.dialect = True

    def param5(self):
        return 1000 + self.function if self.dialect else standard_function(self.function)

    def tick(self, value, hold_s):
        return send_order(self.link, self.param5(), value, hold_s)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        # Термін 0 борт перекладає на «відпустити»; NaN лишає вихід знеструмленим.
        # Тричі — бо сама датаграма відпускання теж може загубитися.
        for _ in range(3):
            send_order(self.link, self.param5(), float('nan'), 0.0, wait=0)
        return False


def run_test(link, function, value, seconds, period=0.1, hold_s=1.0):
    silence = 0
    stop_at = time.monotonic() + seconds
    nxt = time.monotonic()

    with Hold(link, function) as hold:
        while time.monotonic() < stop_at:
            verdict = hold.tick(value, hold_s)

            if verdict in (ACCEPTED, RETRY):
                silence = 0
            elif verdict == SILENCE:
                silence += 1
                if silence * period > 1.0:        # смуга мовчання, не один пропуск
                    print('борт мовчить понад секунду', file=sys.stderr)
                    return 1
            elif verdict == UNSUPPORTED:
                if hold.dialect and standard_function(function) > 0:
                    print('борт не знає діалекту PX4 — пробуємо стандартний номер',
                          file=sys.stderr)
                    hold.dialect = False
                else:
                    print('функцію %d цим протоколом не адресувати' % function,
                          file=sys.stderr)
                    return 1
            else:
                print('відмовлено: апарат armed або запобіжний перемикач не знято',
                      file=sys.stderr)
                return 1

            nxt = max(nxt + period, time.monotonic())  # абсолютний розклад, без зсуву
            time.sleep(max(0.0, nxt - time.monotonic()))

    return 0                                           # __exit__ відпустить сам
