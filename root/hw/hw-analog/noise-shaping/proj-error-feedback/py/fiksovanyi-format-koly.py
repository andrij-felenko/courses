DROP    = 8                        # скільки молодших бітів відкидаємо (16 -> 8)
OUT_MAX = (1 << (16 - DROP)) - 1   # 255 для 8-бітного виходу

def shape2_shift(sample):
    u = sample + 2 * shape2_shift.e1 - shape2_shift.e2

    # округлення до найближчого рівня = додати півкроку (1<<(DROP-1)) і відкинути DROP біт
    level = (u + (1 << (DROP - 1))) >> DROP
    level = max(0, min(level, OUT_MAX))

    y = level << DROP                 # назад у масштаб входу — просто зсув
    e = u - y

    shape2_shift.e2 = shape2_shift.e1
    shape2_shift.e1 = e

    return level

shape2_shift.e1 = shape2_shift.e2 = 0
