in_prev = False   # вхід на попередній ітерації
q       = False   # вихід «тригера»

# викликається часто (в циклі або по перериванню)
def tff_div2(inp):
    global in_prev, q
    rising = inp and not in_prev   # фронт 0→1 саме зараз?
    if rising:
        q = not q                  # toggle: перевернути вихід
    in_prev = inp                  # запам'ятати вхід на наступний крок
    return q                       # q міняється вдвічі рідше за inp
