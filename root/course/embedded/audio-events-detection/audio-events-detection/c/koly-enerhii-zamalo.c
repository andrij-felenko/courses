int zero_crossings(const int16_t *frame, int N) {
    int count = 0;
    for (int i = 1; i < N; i++) {
        // знак змінився ⟺ добуток сусідів від'ємний;
        // порівнюємо через >=0, щоб не множити (та й не переповнити)
        if ((frame[i - 1] >= 0) != (frame[i] >= 0))
            count++;
    }
    return count;                  // 0 … N-1
}
