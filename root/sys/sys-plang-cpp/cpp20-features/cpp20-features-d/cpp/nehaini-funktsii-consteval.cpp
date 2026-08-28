consteval int compile_time_hash(std::string_view str) {
    int hash = 5381;
    for (char c : str) {
        hash = ((hash << 5) + hash) + static_cast<int>(c);
    }
    return hash;
}

constexpr int h1 = compile_time_hash("api_v1"); // Успішно обчислено компілятором
int x = 42;
// int h2 = compile_time_hash(std::to_string(x)); // Помилка компіляції!
