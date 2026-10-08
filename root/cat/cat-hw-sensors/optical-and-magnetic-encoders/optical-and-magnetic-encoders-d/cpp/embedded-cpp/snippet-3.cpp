// Шаблонні inline-функції конвертації коду Ґрея на C++
template <typename T>
constexpr T grayToBinary(T gray) noexcept {
    T mask = gray >> 1;
    while (mask != 0) {
        gray ^= mask;
        mask >>= 1;
    }
    return gray;
}

template <typename T>
constexpr T binaryToGray(T binary) noexcept {
    return binary ^ (binary >> 1);
}
