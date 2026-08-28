/* Двійковий пошук діапазону входжень зразка P довжини M */
typedef struct {
    int left;
    int right;
    int count;
} SearchRange;

SearchRange suffix_array_search(const char *text, int n, const int *sa, const char *pattern, int m) {
    SearchRange res = {-1, -1, 0};
    if (n <= 0 || m <= 0) return res;

    /* 1. Пошук лівої межі */
    int low = 0, high = n - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(text + sa[mid], pattern, (size_t)m);
        if (cmp >= 0) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1 || strncmp(text + sa[first], pattern, (size_t)m) != 0) {
        return res; /* Не знайдено */
    }

    /* 2. Пошук правої межі */
    low = first;
    high = n - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(text + sa[mid], pattern, (size_t)m);
        if (cmp == 0) {
            last = mid;
            low = mid + 1;
        } else if (cmp < 0) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}
