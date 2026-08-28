def deep_clone(value, memo=None):
    if memo is None:
        memo = {}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value                     # примітив — як є
    if id(value) in memo:
        return memo[id(value)]           # вже копіювали — ТА САМА копія

    if isinstance(value, list):
        copy_obj = []
        memo[id(value)] = copy_obj       # ← реєстрація ДО рекурсії рве цикл
        copy_obj.extend(deep_clone(x, memo) for x in value)
        return copy_obj

    cls = value.__class__
    copy_obj = cls.__new__(cls)          # той самий клас, без __init__
    memo[id(value)] = copy_obj           # ← реєстрація ДО рекурсії
    for k, v in value.__dict__.items():
        setattr(copy_obj, k, deep_clone(v, memo))
    return copy_obj
