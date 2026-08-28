static void binary_insertion_sort(int *arr, size_t start, size_t len, size_t sorted_len) {
    for (size_t i = sorted_len; i < len; ++i) {
        int key = arr[start + i];
        // Двійковий пошук точки вставки ключа у відрізку arr[start .. start + i - 1]
        size_t left = start;
        size_t right = start + i;
        while (left < right) {
            size_t mid = left + (right - left) / 2;
            if (key < arr[mid]) {
                right = mid;
            } else {
                left = mid + 1; // Забезпечує стійкість (стабільність) сортування
            }
        }
        // Зсуваємо елементи праворуч для звільнення осередку на позиції left
        size_t count = (start + i) - left;
        if (count > 0) {
            memmove(&arr[left + 1], &arr[left], count * sizeof(int));
        }
        arr[left] = key;
    }
}
