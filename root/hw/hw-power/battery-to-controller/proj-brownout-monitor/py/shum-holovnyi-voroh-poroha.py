# Медіана з 5 відліків: стійка до поодиноких викидів (просадок від сплесків струму).
def median5(a):
    # Проста сортувальна вставка — для 5 елементів швидша й коротша за будь-що інше.
    for i in range(1, 5):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a[2]   # середній елемент відсортованого масиву з 5


def read_vcc_filtered_mv():
    s = [read_vcc_mv() for _ in range(5)]
    return median5(s)
