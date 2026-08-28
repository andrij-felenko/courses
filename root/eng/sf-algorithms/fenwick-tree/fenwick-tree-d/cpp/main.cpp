std::size_t idx = 0;
T current_sum = 0;

for (std::size_t len = max_pow; len > 0; len >>= 1) {
    if (idx + len <= N && current_sum + T[idx + len] < target_sum) {
        idx += len;
        current_sum += T[idx];
    }
}
return idx + 1; // 1-based індекс шуканого елемента
