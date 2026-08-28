// Первинний шаблон
template<typename T>
bool are_equal(T a, T b) {
    return a == b;
}

// Повна спеціалізація для const char*
template<>
bool are_equal<const char*>(const char* a, const char* b) {
    return std::strcmp(a, b) == 0;
}
