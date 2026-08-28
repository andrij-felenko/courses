words = ["A", "B", "C", "D"]
R, C = 4, 8                            # 4 слова по 8 бітів

def per_word_errors(air_positions, interleave):
    """Куди в кодових словах падають помилки з даних позицій ефіру."""
    hits = {w: 0 for w in words}
    for p in air_positions:
        if interleave:
            r = p % R                 # стовпчик за стовпчиком: сусіди — з різних слів
        else:
            r = p // C                # слово за словом: сусіди — з одного слова
        hits[words[r]] += 1
    return hits

burst = [8, 9, 10, 11]                # пачка: 4 біти ефіру підряд

plain = per_word_errors(burst, interleave=False)
inter = per_word_errors(burst, interleave=True)

print("без перемішування:", plain)    # {'A': 0, 'B': 4, 'C': 0, 'D': 0}
print("з перемішуванням: ", inter)    # {'A': 1, 'B': 1, 'C': 1, 'D': 1}
print("найгірше слово без:", max(plain.values()))   # 4  → більше за бюджет (1): МЕРТВЕ
print("найгірше слово з:  ", max(inter.values()))   # 1  → у межах бюджету: ВИПРАВНО
