template <typename T, typename Compare>
void TimSort<T, Compare>::merge_lo(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    if (temp_buf_.size() < len_a) {
        temp_buf_.resize(len_a);
    }
    std::move(data.begin() + base_a, data.begin() + base_a + len_a, temp_buf_.begin());

    size_t cursor_a = 0;
    size_t cursor_b = base_b;
    size_t dest = base_a;
    size_t min_gallop = min_gallop_;

    while (cursor_a < len_a && cursor_b < base_b + len_b) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (comp_(data[cursor_b], temp_buf_[cursor_a])) {
                data[dest++] = std::move(data[cursor_b++]);
                count_b++;
                count_a = 0;
                if (cursor_b == base_b + len_b) goto outer_lo;
            } else {
                data[dest++] = std::move(temp_buf_[cursor_a++]);
                count_a++;
                count_b = 0;
                if (cursor_a == len_a) goto outer_lo;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = gallop_right_impl(data[cursor_b], std::span<const T>(temp_buf_.data(), len_a), cursor_a, len_a - cursor_a, 0, comp_);
            if (count_a > 0) {
                std::move(temp_buf_.begin() + cursor_a, temp_buf_.begin() + cursor_a + count_a, data.begin() + dest);
                dest += count_a;
                cursor_a += count_a;
                if (cursor_a == len_a) goto outer_lo;
            }
            data[dest++] = std::move(data[cursor_b++]);
            if (cursor_b == base_b + len_b) goto outer_lo;

            count_b = gallop_left_impl(temp_buf_[cursor_a], std::span<const T>(data.data(), base_b + len_b), cursor_b, base_b + len_b - cursor_b, 0, comp_);
            if (count_b > 0) {
                std::move(data.begin() + cursor_b, data.begin() + cursor_b + count_b, data.begin() + dest);
                dest += count_b;
                cursor_b += count_b;
                if (cursor_b == base_b + len_b) goto outer_lo;
            }
            data[dest++] = std::move(temp_buf_[cursor_a++]);
            if (cursor_a == len_a) goto outer_lo;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_lo:
    min_gallop_ = (min_gallop < 1) ? 1 : min_gallop;
    if (cursor_a < len_a) {
        std::move(temp_buf_.begin() + cursor_a, temp_buf_.begin() + len_a, data.begin() + dest);
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_hi(std::span<T> data, size_t base_a, size_t len_a, size_t base_b, size_t len_b) {
    if (temp_buf_.size() < len_b) {
        temp_buf_.resize(len_b);
    }
    std::move(data.begin() + base_b, data.begin() + base_b + len_b, temp_buf_.begin());

    size_t cursor_a = base_a + len_a - 1;
    size_t cursor_b = len_b - 1;
    size_t dest = base_b + len_b - 1;
    size_t min_gallop = min_gallop_;

    while (len_a > 0 && len_b > 0) {
        size_t count_a = 0;
        size_t count_b = 0;

        do {
            if (comp_(data[cursor_a], temp_buf_[cursor_b])) {
                data[dest--] = std::move(temp_buf_[cursor_b--]);
                len_b--;
                count_b++;
                count_a = 0;
                if (len_b == 0) goto outer_hi;
            } else {
                data[dest--] = std::move(data[cursor_a--]);
                len_a--;
                count_a++;
                count_b = 0;
                if (len_a == 0) goto outer_hi;
            }
        } while ((count_a | count_b) < min_gallop);

        do {
            count_a = len_a - gallop_right_impl(temp_buf_[cursor_b], std::span<const T>(data.data(), base_a + len_a), base_a, len_a, len_a - 1, comp_);
            if (count_a > 0) {
                dest -= count_a;
                cursor_a -= count_a;
                len_a -= count_a;
                std::move_backward(data.begin() + cursor_a + 1, data.begin() + cursor_a + 1 + count_a, data.begin() + dest + count_a + 1);
                if (len_a == 0) goto outer_hi;
            }
            data[dest--] = std::move(temp_buf_[cursor_b--]);
            len_b--;
            if (len_b == 0) goto outer_hi;

            count_b = len_b - gallop_left_impl(data[cursor_a], std::span<const T>(temp_buf_.data(), len_b), 0, len_b, len_b - 1, comp_);
            if (count_b > 0) {
                dest -= count_b;
                cursor_b -= count_b;
                len_b -= count_b;
                std::move(temp_buf_.begin() + cursor_b + 1, temp_buf_.begin() + cursor_b + 1 + count_b, data.begin() + dest + 1);
                if (len_b == 0) goto outer_hi;
            }
            data[dest--] = std::move(data[cursor_a--]);
            len_a--;
            if (len_a == 0) goto outer_hi;

            min_gallop--;
        } while (count_a >= MIN_GALLOP_DEFAULT || count_b >= MIN_GALLOP_DEFAULT);

        if (min_gallop < 1) min_gallop = 1;
        min_gallop += 2;
    }

outer_hi:
    min_gallop_ = (min_gallop < 1) ? 1 : min_gallop;
    if (len_b > 0) {
        std::move(temp_buf_.begin(), temp_buf_.begin() + len_b, data.begin() + dest - len_b + 1);
    }
}

template <typename T, typename Compare>
void TimSort<T, Compare>::merge_at(std::span<T> data, size_t i) {
    size_t base_a = stack_[i].start;
    size_t len_a = stack_[i].len;
    size_t base_b = stack_[i + 1].start;
    size_t len_b = stack_[i + 1].len;

    stack_[i].len = len_a + len_b;
    if (i == stack_size_ - 3) {
        stack_[i + 1] = stack_[i + 2];
    }
    stack_size_--;

    size_t k = gallop_right_impl(data[base_b], std::span<const T>(data.data(), data.size()), base_a, len_a, 0, comp_);
    base_a += k;
    len_a -= k;
    if (len_a == 0) return;

    len_b = gallop_left_impl(data[base_a + len_a - 1], std::span<const T>(data.data(), data.size()), base_b, len_b, len_b - 1, comp_);
    if (len_b == 0) return;

    if (len_a <= len_b) {
        merge_lo(data, base_a, len_a, base_b, len_b);
    } else {
        merge_hi(data, base_a, len_a, base_b, len_b);
    }
}
