static size_t gallop_right(int key, const int *arr, size_t base, size_t len, size_t hint) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (key < arr[base + hint]) {
        // Галоп вліво від позиції hint
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && key < arr[base + hint - ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        // Галоп вправо від позиції hint
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && key >= arr[base + hint + ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    // Двійковий пошук у локалізованому діапазоні [last_ofs, ofs)
    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (key < arr[base + m]) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}

static size_t gallop_left(int key, const int *arr, size_t base, size_t len, size_t hint) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (key <= arr[base + hint]) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && key <= arr[base + hint - ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && key > arr[base + hint + ofs]) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        last_ofs += hint;
        ofs += hint;
    }

    last_ofs++;
    while (last_ofs < ofs) {
        size_t m = last_ofs + (ofs - last_ofs) / 2;
        if (key <= arr[base + m]) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}
