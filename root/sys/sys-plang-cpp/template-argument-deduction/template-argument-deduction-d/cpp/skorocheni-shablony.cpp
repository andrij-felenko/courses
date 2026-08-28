// Скорочений синтаксис C++20:
void process_item(auto&& item, std::integral auto count) {
    // ...
}

// Повний синтаксичний еквівалент:
template<typename T1, std::integral T2>
void process_item(T1&& item, T2 count) {
    // ...
}
