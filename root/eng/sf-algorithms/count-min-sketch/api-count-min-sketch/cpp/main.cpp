namespace countmin {

enum class Status : int32_t {
    Success           =  0,  // Операцію успішно завершено
    InvalidParam      = -1,  // Некоректний вхідний параметр
    NoMemory          = -2,  // Помилка виділення пам'яті
    DimensionMismatch = -3,  // Невідповідність розмірностей або seed
    BufferTooSmall    = -4,  // Недостатній розмір буфера
    CorruptedData     = -5   // Помилка контрольної суми або пошкодження даних
};

} // namespace countmin
