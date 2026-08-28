v0 = None
for k in [8, 4, 12, 2, 6, 10, 14]:          # база: збалансоване дерево на 7 вузлів
    v0 = insert(v0, k, str(k))

versions = [v0]
versions.append(insert(versions[-1], 15, "15"))   # v1 = v0 + ключ 15
versions.append(insert(versions[-1],  5,  "5"))   # v2 = v1 + ключ 5

print(lookup(versions[0], 15))   # None  — у нульовій версії п'ятнадцяти ще немає
print(lookup(versions[1], 15))   # '15'  — у першій уже є
print(lookup(versions[0],  6))   # '6'   — спільний вузол, читається з обох версій
print(lookup(versions[2],  5))   # '5'
print(lookup(versions[1],  5))   # None  — а у v1 п'ятірки ще не було
