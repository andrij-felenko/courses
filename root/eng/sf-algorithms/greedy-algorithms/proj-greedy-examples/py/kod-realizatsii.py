from typing import List, Dict, Any

def schedule_intervals(intervals: List[Dict[str, int]]) -> List[Dict[str, int]]:
    """
    Знаходить максимальну кількість сумісних інтервалів.
    Кожен інтервал є словником {'id': int, 'start': int, 'finish': int}.
    """
    if not intervals:
        return []

    # Крок 1: Сортування за часом закінчення finish
    sorted_intervals = sorted(intervals, key=lambda x: (x['finish'], x['start']))

    result = []
    # Крок 2: Обираємо перший інтервал
    result.append(sorted_intervals[0])
    last_finish = sorted_intervals[0]['finish']

    # Крок 3: Жадібний вибір наступних сумісних інтервалів
    for interval in sorted_intervals[1:]:
        if interval['start'] >= last_finish:
            result.append(interval)
            last_finish = interval['finish']

    return result


if __name__ == "__main__":
    test_intervals = [
        {'id': 1, 'start': 0, 'finish': 3},
        {'id': 2, 'start': 1, 'finish': 4},
        {'id': 3, 'start': 2, 'finish': 6},
        {'id': 4, 'start': 3, 'finish': 7},
        {'id': 5, 'start': 5, 'finish': 8},
        {'id': 6, 'start': 7, 'finish': 10}
    ]

    selected = schedule_intervals(test_intervals)
    print(f"Обрано інтервалів: {len(selected)}")
    for item in selected:
        print(f"Подія {item['id']}: [{item['start']}, {item['finish']}]")
