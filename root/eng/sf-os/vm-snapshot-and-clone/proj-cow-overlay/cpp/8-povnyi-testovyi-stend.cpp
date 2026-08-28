int main() {
    const std::string base_img = "test_base.raw";
    const std::string snap_img = "test_snap1.cow";
    constexpr uint64_t total_sec = 16;

    // 1. Створюємо базовий образ розміром 16 секторів, заповнений 0xAA
    {
        int base_fd = ::open(base_img.c_str(), O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
        std::array<uint8_t, SECTOR_SIZE> base_data{};
        base_data.fill(0xAA);
        for (size_t i = 0; i < total_sec; ++i) {
            ::pwrite(base_fd, base_data.data(), SECTOR_SIZE, i * SECTOR_SIZE);
        }
        ::close(base_fd);
    }

    // 2. Створюємо оверлей snap1 поверх base
    auto create_res = create_cow_overlay(snap_img, base_img, total_sec);
    if (!create_res) {
        std::cerr << "Помилка створення оверлею: " << create_res.error().message() << '\n';
        return 1;
    }

    // 3. Відкриваємо ланцюжок
    auto chain_res = open_cow_chain(snap_img);
    if (!chain_res) {
        std::cerr << "Помилка відкриття ланцюжка: " << chain_res.error().message() << '\n';
        return 1;
    }
    auto& chain = *chain_res;

    // 4. Записуємо в сектор #3 оверлею значення 0xCC
    std::array<uint8_t, SECTOR_SIZE> mod_data{};
    mod_data.fill(0xCC);
    auto write_res = cow_write_sector(*chain, 3, mod_data);
    if (!write_res) {
        std::cerr << "Помилка запису в сектор 3\n";
        return 1;
    }

    // 5. Читаємо сектор #0 (повинен повернути 0xAA з бази)
    std::array<uint8_t, SECTOR_SIZE> read_buf{};
    cow_read_sector(*chain, 0, read_buf);
    std::cout << "Сектор 0: 0x" << std::hex << static_cast<int>(read_buf[0]) << " (очікується 0xaa)\n";

    // 6. Читаємо сектор #3 (повинен повернути 0xCC з оверлею)
    cow_read_sector(*chain, 3, read_buf);
    std::cout << "Сектор 3: 0x" << std::hex << static_cast<int>(read_buf[0]) << " (очікується 0xcc)\n";

    // 7. Виконуємо Block Commit у базовий образ
    cow_commit_to_backing(*chain);
    chain.reset(); // Закриваємо файлові дескриптори перед перевіркою

    // 8. Перевіряємо, що в базовому образі сектор #3 тепер містить 0xCC
    int base_fd = ::open(base_img.c_str(), O_RDONLY | O_CLOEXEC);
    ::pread(base_fd, read_buf.data(), SECTOR_SIZE, 3 * SECTOR_SIZE);
    std::cout << "База після commit (сектор 3): 0x" << std::hex << static_cast<int>(read_buf[0]) 
              << " (очікується 0xcc)\n" << std::dec;
    ::close(base_fd);

    // Очищення тестових файлів
    ::unlink(snap_img.c_str());
    ::unlink(base_img.c_str());
    return 0;
}
