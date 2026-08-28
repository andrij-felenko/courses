import time

# Повільна база (зсунута ліворуч на 6 — це ділення на 64 у цілих числах)
baseline = measure_pad() << 6   # зберігаємо базу в 64× збільшеному масштабі;
                                # початкова база з першого заміру
TOUCH_DELTA = 12                # поріг стрибка над базою, у одиницях n

while True:
    raw = measure_pad()
    base = baseline >> 6                    # поточна база у звичайних одиницях

    touched = raw > base + TOUCH_DELTA      # дотик = стрибок над базою

    # База доганяє сире значення ПОВІЛЬНО — і лише коли пальця немає,
    # щоб дотик не "розчинився" у підтягнутій базі.
    if not touched:
        baseline += ((raw << 6) - baseline) >> 6

    print("TOUCH" if touched else "----")
    time.sleep_ms(20)                       # ~50 замірів за секунду
