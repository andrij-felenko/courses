_DECODERS = {1: decode_v1, 2: decode_v2, 3: decode_v3}
#   schema:1 — лише миттєве w, інтегруємо самі
#   schema:2 — wh накопичувальний лічильник
#   schema:3 — wh дельта за інтервал ← новий сенс, нова версія

def decode(r: dict) -> Reading:
    try:
        return _DECODERS[r["schema"]](r)     # сенс wh — за версією запису
    except KeyError:
        raise ValueError(f'нема декодера для schema:{r["schema"]}')
