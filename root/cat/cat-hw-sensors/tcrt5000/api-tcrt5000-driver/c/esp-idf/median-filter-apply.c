#define FILTER_WINDOW_SIZE 5

typedef struct {
    uint16_t buffer[FILTER_WINDOW_SIZE];
    uint8_t index;
    uint8_t count;
} median_filter_t;

// Додавання відліку та отримання медіани
uint16_t median_filter_apply(median_filter_t *f, uint16_t input) {
    f->buffer[f->index] = input;
    f->index = (f->index + 1) % FILTER_WINDOW_SIZE;
    if (f->count < FILTER_WINDOW_SIZE) f->count++;

    uint16_t temp[FILTER_WINDOW_SIZE];
    for (uint8_t i = 0; i < f->count; i++) temp[i] = f->buffer[i];

    // Сортування вставками
    for (uint8_t i = 1; i < f->count; i++) {
        uint16_t key = temp[i];
        int j = i - 1;
        while (j >= 0 && temp[j] > key) {
            temp[j + 1] = temp[j];
            j--;
        }
        temp[j + 1] = key;
    }
    return temp[f->count / 2];
}

// Отримання фільтрованого значення в драйвері TCRT5000
tcrt5000_err_t tcrt5000_read_filtered(tcrt5000_t *dev, median_filter_t *m_filt, uint16_t *filtered_out) {
    uint16_t raw;
    tcrt5000_err_t err = tcrt5000_read_analog_raw(dev, &raw);
    if (err != TCRT5000_OK) return err;

    uint16_t med = median_filter_apply(m_filt, raw);
    
    // Експоненційне скользяче усереднення (EMA)
    if (dev->filtered_value == 0) {
        dev->filtered_value = med;
    } else {
        dev->filtered_value = (uint16_t)((0.3f * med) + (0.7f * dev->filtered_value));
    }

    *filtered_out = dev->filtered_value;
    return TCRT5000_OK;
}
