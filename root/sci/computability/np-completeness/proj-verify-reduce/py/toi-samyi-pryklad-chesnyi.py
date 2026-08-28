def find_subset_sum(numbers, target):
    n = len(numbers)
    for mask in range(1 << n):                 # усі 2ⁿ підмножин
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += numbers[i]
        if s == target:
            return [numbers[i] for i in range(n) if mask & (1 << i)]
    return None                                # жодна підмножина не підійшла
