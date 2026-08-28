void min_heap_build(int *arr, int n) {
    for (int i = (n / 2) - 1; i >= 0; --i) {
        int curr = i;
        while (2 * curr + 1 < n) {
            int left = 2 * curr + 1;
            int right = 2 * curr + 2;
            int smallest = left;

            if (right < n && arr[right] < arr[left]) {
                smallest = right;
            }
            if (arr[smallest] < arr[curr]) {
                int temp = arr[curr];
                arr[curr] = arr[smallest];
                arr[smallest] = temp;
                curr = smallest;
            } else {
                break;
            }
        }
    }
}
