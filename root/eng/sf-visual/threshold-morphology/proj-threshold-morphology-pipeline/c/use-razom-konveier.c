// Повний конвеєр: сірий кадр → чиста маска + площа виділеного.
// Буфери buf_a/buf_b/I/mask — статичні (без malloc), живуть увесь час роботи.
uint32_t pipeline(const uint8_t gray[H][W], uint8_t mask[H][W]) {
    build_integral(gray);                      // 1. таблиця сум для адаптивного порога
    adaptive_threshold(gray, buf_a);           // 2. сира маска → buf_a

    opening3(buf_a, buf_b, mask);              // 3. відкриття: buf_a → buf_b (tmp = mask)
    closing3(buf_b, mask, buf_a);              // 4. закриття: buf_b → mask  (tmp = buf_a)

    return count_white(mask);                  // 5. площа виділеного
}
