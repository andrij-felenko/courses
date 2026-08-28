/* Прикладний виклик підтвердження прошивки після самотестування на C99 */
bool ota_confirm_running_image(void) {
    boot_record_t rec0, rec1;
    flash_read(SECTOR_0_ADDR, &rec0, sizeof(boot_record_t));
    flash_read(SECTOR_1_ADDR, &rec1, sizeof(boot_record_t));

    bool valid0 = is_record_valid(&rec0);
    bool valid1 = is_record_valid(&rec1);

    boot_record_t current;
    if (valid0 && valid1) {
        current = (rec0.sequence >= rec1.sequence) ? rec0 : rec1;
    } else if (valid0) {
        current = rec0;
    } else if (valid1) {
        current = rec1;
    } else {
        return false;
    }

    /* Якщо ми стартували у випробувальному стані, закріплюємо успіх */
    if (current.status == STATE_PENDING_TEST) {
        current.status = (uint8_t)STATE_CONFIRMED_OK;
        current.retries_left = 0;
        return boot_metadata_write(&current);
    }

    return true;
}
