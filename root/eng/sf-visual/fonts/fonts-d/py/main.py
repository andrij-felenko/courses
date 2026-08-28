from bisect import bisect_left

# table — відсортований список пар (key, adjust), де key = (left << 8) | right.
# keys — паралельний список самих ключів для двійкового пошуку через bisect.
def kern(table, keys, left, right):
    key = (left << 8) | right
    i = bisect_left(keys, key)               # двійковий пошук O(log n)
    if i < len(keys) and keys[i] == key:
        return table[i][1]                   # знайшли пару — повертаємо поправку
    return 0                                 # пари нема — кернінгу немає
