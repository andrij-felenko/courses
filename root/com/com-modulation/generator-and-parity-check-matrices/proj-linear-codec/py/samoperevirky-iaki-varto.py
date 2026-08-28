# [7, 4]: рядки P скопійовані з матриці рівно так, як вона надрукована
code = LinearCode(7, 4, [bits("110"), bits("011"), bits("111"), bits("101")])

# Самоперевірка 1: H·Gᵀ = 0 — кожен рядок G мусить бути кодовим словом.
assert all(code.syndrome(code.encode(1 << j)) == 0 for j in range(code.k))

# Самоперевірка 2: будь-яка одинична помилка декодується сама в себе.
# Синдром не залежить від даних, тож нульового слова досить для всіх 2ᵏ.
zero = code.encode(0)
assert all(code.decode(zero ^ (1 << i)) == (0, 1 << i) for i in range(code.n))

# Робочий приклад.
m = bits("1011")
c = code.encode(m)                       # 1011100: дані + три біти надлишку
r = c ^ (1 << 2)                         # канал перевернув біт з індексом 2
data, e = code.decode(r)
assert (data, e) == (m, 1 << 2)          # дані цілі, помилку названо
assert code.syndrome_by_rows(r) == code.syndrome(r)   # обидва шляхи згодні
