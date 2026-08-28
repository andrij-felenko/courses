std::error_code ec;

// 1. Створення каталогів
fs::create_directories("/tmp/cache/levels/a/b", ec);
if (ec) {
    // Обробка помилки ОС без винятків
}

// 2. Перевірка статусу та розміру
if (fs::exists("/tmp/cache", ec) && fs::is_directory("/tmp/cache", ec)) {
    fs::space_info space = fs::space("/tmp/cache", ec);
    // space.capacity, space.free, space.available
}

// 3. Копіювання та видалення
fs::copy_file("/tmp/source.bin", "/tmp/dest.bin", fs::copy_options::overwrite_existing, ec);
fs::remove_all("/tmp/cache", ec);
