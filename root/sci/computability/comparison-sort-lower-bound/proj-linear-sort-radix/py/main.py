from typing import List

def counting_sort(arr: List[int]) -> List[int]:
    """Сортування підрахунком для невід'ємних цілих чисел."""
    if not arr:
        return []

    max_val = max(arr)
    count = [0] * (max_val + 1)
    output = [0] * len(arr)

    # Підрахунок частот
    for x in arr:
        count[x] += 1

    # Префіксні суми
    for i in range(1, max_val + 1):
        count[i] += count[i - 1]

    # Запис у вихідний масив із кінця (стабільність)
    for x in reversed(arr):
        output[count[x] - 1] = x
        count[x] -= 1

    return output


def radix_sort_u32(arr: List[int]) -> List[int]:
    """Порозрядне сортування (LSD Radix Sort) для 32-бітних чисел по 8 бітів."""
    if len(arr) <= 1:
        return list(arr)

    res = list(arr)
    n = len(res)

    # 4 проходи (по 8 бітів: 0, 8, 16, 24)
    for shift in range(0, 32, 8):
        count = [0] * 256
        temp = [0] * n

        # Підрахунок частот для поточного байта
        for x in res:
            byte_val = (x >> shift) & 0xFF
            count[byte_val] += 1

        # Префіксні суми
        total = 0
        for i in range(256):
            old_c = count[i]
            count[i] = total
            total += old_c

        # Розподіл елементів
        for x in res:
            byte_val = (x >> shift) & 0xFF
            temp[count[byte_val]] = x
            count[byte_val] += 1

        res = temp

    return res


# Перевірка роботи
if __name__ == "__main__":
    data = [0x00A1F012, 0x00000005, 0x12345678, 0x00A1E000, 0x00000001]
    print("Початковий масив:", [hex(x) for x in data])
    sorted_data = radix_sort_u32(data)
    print("Відсортований масив:", [hex(x) for x in sorted_data])
