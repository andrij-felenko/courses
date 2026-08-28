# Розібрати "D[7..0]" → BusName("D", 7, 0, True).
# Запис без дужок ("CLK") — це скаляр: BusName("CLK", 0, 0, False).
# Кривий запис ("D[7..]", "D[a..b]") — повертаємо None, хай редактор лається.
def parse_bus(s):
    lb = s.find('[')
    if lb == -1:                             # дужок нема — звичайний скаляр
        return BusName(s)

    dd = s.find('..', lb + 1)                # роздільник діапазону
    rb = s.find(']', lb + 1)                 # закрита дужка
    if dd == -1 or rb == -1 or not (lb < dd < rb):
        return None                          # нема "..", нема "]", або переплутаний порядок

    a = s[lb + 1:dd]                          # між '[' і '..'
    b = s[dd + 2:rb]                          # між '..' і ']'
    try:
        left, right = int(a), int(b)         # ValueError, якщо не число
    except ValueError:
        return None                          # "[a..b]" — не діапазон
    return BusName(s[:lb], left, right, True)
