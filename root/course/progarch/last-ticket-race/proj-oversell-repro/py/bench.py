# bench.py — python bench.py   (драйвер: pip install "psycopg[binary]")
import threading
from concurrent.futures import ThreadPoolExecutor
import psycopg  # psycopg 3

DSN     = "postgres://race:race@localhost:5432/race"
CLIENTS = 50   # N покупців на ОДИН квиток (тримаємось під max_connections = 100)
TRIALS  = 20   # скільки разів повторити наліт

# НАЇВНО: read-modify-write, де «рахунок» робить ЗАСТОСУНОК, не SQL.
def naive(conn, buyer):
    seats = conn.execute("SELECT seats_left FROM events WHERE id = 1").fetchone()[0]
    if seats <= 0:                    # рішення на щойно прочитаному (застарілому) числі
        return
    new = seats - 1                   # рахунок у пам'яті застосунку: 1 − 1 = 0
    conn.execute("UPDATE events SET seats_left = %s WHERE id = 1", (new,))
    conn.execute("INSERT INTO bookings (event_id, buyer) VALUES (1, %s)", (buyer,))

# ЗАХИЩЕНО: рішення ухвалює СХОВИЩЕ — атомний UPDATE із вартовим.
def guarded(conn, buyer):
    cur = conn.execute(
        "UPDATE events SET seats_left = seats_left - 1 "
        "WHERE id = 1 AND seats_left > 0")
    if cur.rowcount == 0:             # вартовий 0 > 0 хибний — місць уже немає
        return
    conn.execute("INSERT INTO bookings (event_id, buyer) VALUES (1, %s)", (buyer,))

def stampede(admin, strat):
    admin.execute("UPDATE events SET seats_left = 1 WHERE id = 1")
    admin.execute("TRUNCATE bookings")

    barrier = threading.Barrier(CLIENTS)   # усі CLIENTS зустрічаються тут і рушають РАЗОМ

    def one_buyer(buyer):
        # КОЖЕН покупець — СВОЄ з'єднання; autocommit, щоб кожен крок фіксувався одразу
        with psycopg.connect(DSN, autocommit=True) as conn:
            barrier.wait()                 # ← бар'єр: чекаємо, доки на лінію стануть усі 50
            strat(conn, buyer)

    with ThreadPoolExecutor(max_workers=CLIENTS) as pool:
        list(pool.map(one_buyer, range(CLIENTS)))

    counter = admin.execute("SELECT seats_left FROM events WHERE id = 1").fetchone()[0]
    sold    = admin.execute("SELECT count(*) FROM bookings").fetchone()[0]
    return counter, sold

def main():
    with psycopg.connect(DSN, autocommit=True) as admin:
        print(f"{'стратегія':<10}{'продано':>10}{'зайвих':>10}{'лічильник':>12}")
        for name, strat in (("наївно", naive), ("вартовий", guarded)):
            total_sold = oversold = counter = 0
            for _ in range(TRIALS):
                counter, sold = stampede(admin, strat)
                total_sold += sold
                oversold   += max(0, sold - 1)     # «зайві» понад єдине місце
            print(f"{name:<10}{total_sold:>10}{oversold:>10}{counter:>12}"
                  f"   (за {TRIALS} нальотів)")

if __name__ == "__main__":
    main()
