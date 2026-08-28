from collections import Counter

R = range(1, 11)
prod = Counter(s * o * d for s in R for o in R for d in R)

print("трійок:", 10 ** 3)                                    # 1000
print("різних значень RPN:", len(prod))                      # 120
print("недосяжних цілих у [1,1000]:", 1000 - len(prod))      # 880
print("перші недосяжні:", [n for n in range(1, 30) if n not in prod][:6])
# [11, 13, 17, 19, 22, 23]
