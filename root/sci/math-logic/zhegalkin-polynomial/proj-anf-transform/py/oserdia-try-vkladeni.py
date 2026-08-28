maj = [0, 0, 0, 1, 0, 1, 1, 1]        # МАЖ(a,b,c), рядки 000..111
coef = anf_transform(maj[:])          # копія: перетворення псує вхід (на місці)
print(coef)                           # [0, 0, 0, 1, 0, 1, 1, 0]

names = "cba"                          # домовленість: біт 0 → c, біт 1 → b, біт 2 → a
terms = []
for m, c in enumerate(coef):
    if c:                              # коефіцієнт увімкнено — моном входить у поліном
        vs = [names[i] for i in range(3) if m >> i & 1]
        terms.append("·".join(reversed(vs)) or "1")
print(" ⊕ ".join(terms))              # b·c ⊕ a·c ⊕ a·b
