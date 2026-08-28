template<typename InputIt, typename T>
InputIt find(InputIt first, InputIt last, const T& value) {
    while (first != last) {
        if (*first == value) {
            return first;
        }
        ++first;
    }
    return first;
}
