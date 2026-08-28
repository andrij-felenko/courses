BAL_THRESH_MV = 15      # поріг розбалансу, мВ

def balance_decide(v_mV):
    """v_mV — напруги всіх комірок стосу з монітора, у мВ.
    Повертає маску: біт i == 1 → зливати комірку i."""
    v_min = min(v_mV)                       # найнижча комірка

    mask = 0
    for i, v in enumerate(v_mV):
        if v - v_min > BAL_THRESH_MV:       # втекла більш ніж на поріг
            mask |= 1 << i

    return mask                             # цю маску хост запише в чип
