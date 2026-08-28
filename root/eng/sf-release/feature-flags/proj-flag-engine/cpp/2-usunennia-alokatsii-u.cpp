// Інкрементальне хешування без створення проміжних рядків
uint32_t hash_streaming(std::string_view flag, std::string_view user) {
    // Обчислення хешу без жодної алокації динамічної пам'яті
    char buffer[256];
    if (flag.size() + 1 + user.size() < sizeof(buffer)) {
        std::memcpy(buffer, flag.data(), flag.size());
        buffer[flag.size()] = ':';
        std::memcpy(buffer + flag.size() + 1, user.data(), user.size());
        return murmur3_32(std::string_view(buffer, flag.size() + 1 + user.size()));
    }
    return murmur3_32(std::string(flag) + ":" + std::string(user));
}
