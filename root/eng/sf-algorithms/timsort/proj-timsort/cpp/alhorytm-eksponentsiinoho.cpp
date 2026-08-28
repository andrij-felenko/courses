template <typename T, typename Compare>
size_t gallop_right_impl(const T &key, std::span<const T> arr, size_t base, size_t len, size_t hint, Compare comp) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (comp(key, arr[base + hint])) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && comp(key, arr[base + hint - ofs])) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && !comp(key, arr[base + hint + ofs])) {
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
        if (comp(key, arr[base + m])) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}

template <typename T, typename Compare>
size_t gallop_left_impl(const T &key, std::span<const T> arr, size_t base, size_t len, size_t hint, Compare comp) {
    size_t ofs = 1;
    size_t last_ofs = 0;

    if (!comp(arr[base + hint], key)) {
        size_t max_ofs = hint + 1;
        while (ofs < max_ofs && !comp(arr[base + hint - ofs], key)) {
            last_ofs = ofs;
            ofs = (ofs << 1) + 1;
        }
        if (ofs > max_ofs) ofs = max_ofs;

        size_t tmp = last_ofs;
        last_ofs = hint + 1 - ofs;
        ofs = hint + 1 - tmp;
    } else {
        size_t max_ofs = len - hint;
        while (ofs < max_ofs && comp(arr[base + hint + ofs], key)) {
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
        if (!comp(arr[base + m], key)) {
            ofs = m;
        } else {
            last_ofs = m + 1;
        }
    }
    return ofs;
}
