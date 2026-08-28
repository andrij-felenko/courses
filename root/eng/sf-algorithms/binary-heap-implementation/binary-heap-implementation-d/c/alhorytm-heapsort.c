void heapsort(int *arr, int n) {
    if (n <= 1) return;

    // Фаза 1: побудова Max-купи за O(N)
    for (int i = (n / 2) - 1; i >= 0; --i) {
        int curr = i;
        while (2 * curr + 1 < n) {
            int left = 2 * curr + 1;
            int right = 2 * curr + 2;
            int largest = left;

            if (right < n && arr[right] > arr[left]) {
                largest = right;
            }
            if (arr[largest] > arr[curr]) {
                int temp = arr[curr];
                arr[curr] = arr[largest];
                arr[largest] = temp;
                curr = largest;
            } else {
                break;
            }
        }
    }

    // Фаза 2: послідовне вилучення максимуму за O(N log N)
    for (int end = n - 1; end > 0; --end) {
        int temp = arr[0];
        arr[0] = arr[end];
        arr[end] = temp;

        int curr = 0;
        while (2 * curr + 1 < end) {
            int left = 2 * curr + 1;
            int right = 2 * curr + 2;
            int largest = left;

            if (right < end && arr[right] > arr[left]) {
                largest = right;
            }
            if (arr[largest] > arr[curr]) {
                int t = arr[curr];
                arr[curr] = arr[largest];
                arr[largest] = t;
                curr = largest;
            } else {
                break;
            }
        }
    }
}
