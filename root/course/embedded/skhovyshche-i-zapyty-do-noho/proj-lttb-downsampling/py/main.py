from typing import List, Tuple

def lttb_downsample(data: List[Tuple[float, float]], threshold: int) -> List[Tuple[float, float]]:
    """
    Проріджування часового ряду алгоритмом LTTB.
    :param data: список пар (timestamp, value), відсортований за часом.
    :param threshold: бажана кількість точок на виході (K).
    :return: проріджений список пар довжиною threshold.
    """
    n = len(data)
    if threshold >= n or threshold < 3:
        return data

    sampled: List[Tuple[float, float]] = [data[0]]
    bucket_size = (n - 2) / (threshold - 2)

    a_idx = 0  # Індекс зафіксованої точки попереднього кроку (A)

    for i in range(threshold - 2):
        # Межі поточного бакета
        curr_start = int((i * bucket_size) + 1)
        curr_end = int(((i + 1) * bucket_size) + 1)
        curr_end = min(curr_end, n)

        # Межі наступного бакета для обчислення центру мас (C)
        next_start = int(((i + 1) * bucket_size) + 1)
        next_end = int(((i + 2) * bucket_size) + 1)
        next_end = min(next_end, n)

        # Розрахунок центру мас C(avg_t, avg_v)
        avg_t = 0.0
        avg_v = 0.0
        next_count = next_end - next_start

        if next_count > 0:
            for j in range(next_start, next_end):
                avg_t += data[j][0]
                avg_v += data[j][1]
            avg_t /= next_count
            avg_v /= next_count
        else:
            avg_t = data[-1][0]
            avg_v = data[-1][1]

        # Пошук точки P у поточному бакеті з максимальною площею трикутника
        a_t, a_v = data[a_idx]
        max_area = -1.0
        max_idx = curr_start

        for p_idx in range(curr_start, curr_end):
            p_t, p_v = data[p_idx]
            # Подвійна площа трикутника APC
            area = abs((a_t - avg_t) * (p_v - a_v) - (a_t - p_t) * (avg_v - a_v))
            if area > max_area:
                max_area = area
                max_idx = p_idx

        sampled.append(data[max_idx])
        a_idx = max_idx  # Вибрана точка стає точкою A на наступній ітерації

    sampled.append(data[-1])  # Остання точка ряду
    return sampled
