# Спрощений АЛП: одна лінія sub перемикає додавання/віднімання.
# Повертає 8-бітний результат і перенос-вихід (result, cout).
def alu_addsub(a, b, sub):
    b_eff = b ^ (0xFF if sub else 0x00)  # sub=1 інвертує всі біти B (~B)
    wide = a + b_eff + sub               # +sub додає ту саму +1
    cout = (wide >> 8) & 1               # 9-й біт — перенос-вихід
    return wide & 0xFF, cout             # молодші 8 бітів — результат


r, carry = alu_addsub(7, 5, 1)           # 7 − 5
print(f"7 - 5 = {r}, carry={carry}")     # 7 - 5 = 2, carry=1
