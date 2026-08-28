struct FileBuffer {
    char data[1024];
    constexpr FileBuffer() : data{} {}
    ~FileBuffer() {
        // Нетривіальний деструктор: наприклад, скидання даних у файл
    }
};

// ПОМИЛКА КОМПІЛЯЦІЇ: constexpr об'єкт статичної тривалості не може мати нетривіальний деструктор!
// constexpr FileBuffer g_bad_buf{};
