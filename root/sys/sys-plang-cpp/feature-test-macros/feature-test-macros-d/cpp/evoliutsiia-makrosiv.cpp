#if defined(__cpp_lib_ranges) && __cpp_lib_ranges >= 202207L
    // Лаконічний конвеєр C++23
    auto zipped = std::views::zip(keys, values);
#else
    // Традиційна ітерація C++20 через індекси
    std::vector<std::pair<Key, Value>> zipped;
    for (std::size_t i = 0; i < std::min(keys.size(), values.size()); ++i) {
        zipped.emplace_back(keys[i], values[i]);
    }
#endif
