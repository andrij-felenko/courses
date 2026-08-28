# Танкове змішування: одна ручка → дві швидкості моторів (−100..+100 кожна).
def tank_mix():
    drive = read_axis(vertical)         # вперед/назад: спільна складова
    turn  = read_axis(horizontal)       # ліворуч/праворуч: різницева складова

    left  = drive + turn                # праворуч → лівий мотор швидше
    right = drive - turn                # ... а правий повільніше

    left  = max(-100, min(100, left))
    right = max(-100, min(100, right))
    return left, right
