// Структура лічильників статистики scrub у ядрі Linux (наведено головні поля; у справжньому
// оголошенні між verify_errors та uncorrectable_errors стоять ще no_csum, csum_discards,
// super_errors і malloc_errors)
struct btrfs_scrub_progress {
    __u64 data_extents_scrubbed;  // Кількість просканованих екстентів даних
    __u64 tree_extents_scrubbed;  // Кількість просканованих вузлів B-дерев метаданих
    __u64 data_bytes_scrubbed;    // Загальний обсяг просканованих байтів даних
    __u64 tree_bytes_scrubbed;    // Загальний обсяг просканованих байтів метаданих
    __u64 read_errors;            // Апаратні помилки зчитування з диска (I/O Errors)
    __u64 csum_errors;            // Помилки незбігу контрольних сум CRC32c / xxHash / SHA256
    __u64 verify_errors;          // Помилки валідації заголовків метаданих (bad generation/owner)
    __u64 uncorrectable_errors;   // Фатальні помилки, які не вдалося відновити з RAID-копій!
    __u64 corrected_errors;       // Успішно відновлені спотворення завдяки самовідновленню з RAID-дзеркала
    __u64 last_physical;          // Останній фізичний сектор, оброблений на пристрої
    __u64 unverified_errors;      // Непідтверджені збої читання
};
