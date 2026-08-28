def insert_order(objs, refs):
    # refs[u] = множина об'єктів, на які посилається u (його батьки)
    waiting = {u: set(refs[u]) for u in objs}
    ready = [u for u in objs if not waiting[u]]   # ті, хто вже ні на кого не чекає
    order = []
    while ready:
        v = ready.pop()
        order.append(v)                            # усі батьки v уже в order — вставляти можна
        for u in objs:                             # (у справжній реалізації — зворотний список сусідів)
            if v in waiting[u]:
                waiting[u].discard(v)
                if not waiting[u]:
                    ready.append(u)
    if len(order) != len(objs):
        raise CycleError("зовнішні ключі утворюють цикл")   # лишилися невичерпані залежності
    return order                                    # вставляти в цьому порядку; видаляти — у зворотному
