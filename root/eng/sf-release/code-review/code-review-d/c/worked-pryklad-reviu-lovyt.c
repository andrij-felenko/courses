// Лічильник перезавантажень: читаємо, +1, пишемо назад.
uint32_t bump_boot_count(void) {
    uint32_t count = 0;
    nvs_handle_t h;
    nvs_open("storage", NVS_READWRITE, &h);
    nvs_get_u32(h, "boot_cnt", &count);   // читаємо старе значення
    count++;
    nvs_set_u32(h, "boot_cnt", count);    // пишемо нове
    nvs_commit(h);
    nvs_close(h);
    return count;
}
