WHEEL_SIZE = 256                 # степінь двійки → mod = маска

class Timer:
    def __init__(self, cb, arg):
        self.rounds = 0          # скільки повних кіл ще чекати
        self.cb = cb             # що зробити, коли настане час
        self.arg = arg
        self.next = None         # наступний у тому ж слоті

wheel = [None] * WHEEL_SIZE
cursor = 0                       # «стрілка» — поточний слот

# запланувати подію через delta тіків
def schedule(t, delta):
    slot = (cursor + delta) & (WHEEL_SIZE - 1)
    t.rounds = delta // WHEEL_SIZE   # повних обертів колеса
    t.next = wheel[slot]             # вставляємо в голову списку слота — O(1)
    wheel[slot] = t

# викликати рівно раз на тік (з обробника системного тіку)
def tick():
    global cursor
    cursor = (cursor + 1) & (WHEEL_SIZE - 1)
    prev, t = None, wheel[cursor]    # ідемо лише по ОДНОМУ слоту
    while t:
        if t.rounds == 0:
            nxt = t.next             # знімаємо зі слота
            if prev is None:
                wheel[cursor] = nxt
            else:
                prev.next = nxt
            t.cb(t.arg)              # час настав — запускаємо
            t = nxt
        else:
            t.rounds -= 1            # ще одне коло перечекати
            prev, t = t, t.next
