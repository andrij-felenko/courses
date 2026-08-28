std::initializer_list<int> get_numbers() {
    return {10, 20, 30}; // Помилка: прихований масив знищується на виході з функції!
}

void use_list() {
    auto list = get_numbers();
    for (int x : list) { // Use-After-Free: читання мертвого стекового масиву
        std::cout << x << ' ';
    }
}
