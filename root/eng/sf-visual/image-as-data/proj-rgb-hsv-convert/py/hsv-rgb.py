# HSV (кожен 0..255, тон — увесь круг у байт) -> RGB888. Без float, без ділення в циклі.
def hsv_to_rgb_u8(h, s, v):
    if s == 0:
        return v, v, v                          # сіре: усі канали = V

    region = h // 43                    # 256/6 ≈ 43 → номер сектора 0..5
    rem    = (h - region * 43) * 6              # залишок у 0..255 усередині сектора

    p = (v * (255 - s)) >> 8                                # нижній рівень
    q = (v * (255 - ((s * rem) >> 8))) >> 8                 # спадна складова
    t = (v * (255 - ((s * (255 - rem)) >> 8))) >> 8         # висхідна складова

    if   region == 0: return v, t, p
    elif region == 1: return q, v, p
    elif region == 2: return p, v, t
    elif region == 3: return p, q, v
    elif region == 4: return t, p, v
    else:             return v, p, q            # region 5
