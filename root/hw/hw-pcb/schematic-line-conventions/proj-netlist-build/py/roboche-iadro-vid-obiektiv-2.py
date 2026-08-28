# Чи лежить точка p на ВІДРІЗКУ дроту w (включно з кінцями)?
# Дроти на схемі ортогональні, тож достатньо розглянути H- і V-випадки.
def point_on_wire(p: Point, w: Wire) -> bool:
    if w.a.y == w.b.y:                                     # горизонтальний
        if p.y != w.a.y:
            return False
        return min(w.a.x, w.b.x) <= p.x <= max(w.a.x, w.b.x)
    if w.a.x == w.b.x:                                     # вертикальний
        if p.x != w.a.x:
            return False
        return min(w.a.y, w.b.y) <= p.y <= max(w.a.y, w.b.y)
    # навскісний дріт — рідкість; повна перевірка колінеарності + меж:
    cross = (p.x - w.a.x) * (w.b.y - w.a.y) \
          - (p.y - w.a.y) * (w.b.x - w.a.x)
    if cross != 0:
        return False
    return (min(w.a.x, w.b.x) <= p.x <= max(w.a.x, w.b.x)
            and min(w.a.y, w.b.y) <= p.y <= max(w.a.y, w.b.y))
