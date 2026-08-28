static size_t calculate_minrun(size_t n) {
    size_t r = 0;
    while (n >= 64) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

static size_t count_and_reverse_run(int *arr, size_t start, size_t n) {
    if (start >= n) return 0;
    if (start == n - 1) return 1;

    size_t run_len = 2;
    if (arr[start + 1] < arr[start]) {
        // Строго спадна серія: шукаємо межу, поки елементи зменшуються
        while (start + run_len < n && arr[start + run_len] < arr[start + run_len - 1]) {
            run_len++;
        }
        // Розвертаємо серію на місці
        size_t left = start;
        size_t right = start + run_len - 1;
        while (left < right) {
            int tmp = arr[left];
            arr[left] = arr[right];
            arr[right] = tmp;
            left++;
            right--;
        }
    } else {
        // Неспадна серія
        while (start + run_len < n && arr[start + run_len] >= arr[start + run_len - 1]) {
            run_len++;
        }
    }
    return run_len;
}
