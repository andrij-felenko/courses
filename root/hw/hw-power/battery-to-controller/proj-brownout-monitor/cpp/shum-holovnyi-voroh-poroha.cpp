// Медіана з 5 відліків: стійка до поодиноких викидів (просадок від сплесків струму).
static uint16_t median5(uint16_t *a) {
    // Проста сортувальна вставка — для 5 елементів швидша й коротша за будь-що інше.
    for (uint8_t i = 1; i < 5; i++) {
        uint16_t key = a[i];
        int8_t j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = key;
    }
    return a[2];   // середній елемент відсортованого масиву з 5
}

uint16_t read_vcc_filtered_mv(void) {
    uint16_t s[5];
    for (uint8_t i = 0; i < 5; i++) s[i] = read_vcc_mv();
    return median5(s);
}
