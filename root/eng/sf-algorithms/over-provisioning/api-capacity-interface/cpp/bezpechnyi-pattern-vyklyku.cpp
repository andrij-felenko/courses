// ІДІОМАТИЧНЕ БЕЗПЕЧНЕ РОЗШИРЕННЯ У C++ (RAII):
try {
    std::size_t new_cap = capacity + (capacity >> 1); // Геометричний ріст x1.5
    auto new_data = std::make_unique<int[]>(new_cap);
    std::copy(data.get(), data.get() + size, new_data.get());
    data = std::move(new_data);
    capacity = new_cap;
} catch (const std::bad_alloc&) {
    std::cerr << "Помилка: не вдалося виділити пам'ять у C++\n";
    return false;
}
