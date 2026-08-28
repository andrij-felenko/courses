int main(void) {
    const char *base_img = "test_base.raw";
    const char *snap_img = "test_snap1.cow";
    const uint64_t total_sec = 16;

    // 1. Створюємо базовий образ розміром 16 секторів, заповнений 0xAA
    int base_fd = open(base_img, O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    uint8_t base_data[SECTOR_SIZE];
    memset(base_data, 0xAA, sizeof(base_data));
    for (int i = 0; i < (int)total_sec; ++i) {
        pwrite(base_fd, base_data, SECTOR_SIZE, i * SECTOR_SIZE);
    }
    close(base_fd);

    // 2. Створюємо оверлей snap1 поверх base
    if (cow_create_overlay(snap_img, base_img, total_sec) != 0) {
        fprintf(stderr, "Помилка створення оверлею\n");
        return 1;
    }

    // 3. Відкриваємо ланцюжок
    CowNode *chain = cow_open_chain(snap_img);
    if (!chain) {
        fprintf(stderr, "Помилка відкриття ланцюжка\n");
        return 1;
    }

    // 4. Записуємо в сектор #3 оверлею значення 0xCC
    uint8_t mod_data[SECTOR_SIZE];
    memset(mod_data, 0xCC, sizeof(mod_data));
    cow_write_sector(chain, 3, mod_data);

    // 5. Читаємо сектор #0 (повинен повернути 0xAA з бази)
    uint8_t read_buf[SECTOR_SIZE];
    cow_read_sector(chain, 0, read_buf);
    printf("Сектор 0: 0x%02X (очікується 0xAA)\n", read_buf[0]);

    // 6. Читаємо сектор #3 (повинен повернути 0xCC з оверлею)
    cow_read_sector(chain, 3, read_buf);
    printf("Сектор 3: 0x%02X (очікується 0xCC)\n", read_buf[0]);

    // 7. Виконуємо Block Commit у базовий образ
    cow_commit_to_backing(chain);
    cow_close_chain(chain);

    // 8. Перевіряємо, що в базовому образі сектор #3 тепер містить 0xCC
    base_fd = open(base_img, O_RDONLY | O_CLOEXEC);
    pread(base_fd, read_buf, SECTOR_SIZE, 3 * SECTOR_SIZE);
    printf("База після commit (сектор 3): 0x%02X (очікується 0xCC)\n", read_buf[0]);
    close(base_fd);

    // Очищення тестових файлів
    unlink(snap_img);
    unlink(base_img);
    return 0;
}
