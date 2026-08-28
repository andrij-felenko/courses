typedef uint16_t signal_t;

typedef struct {
    signal_t sig;       // Числовий ідентифікатор сигналу
    uint16_t len;       // Довжина корисного навантаження в байтах
    union {
        uint32_t u32;   // Скалярний параметр
        int32_t  i32;   // Знакове числове значення
        void    *ptr;   // Вказівник на статичний блок пам'яті
        uint8_t  raw[8];// Масив сирих байтів
    } param;
} event_t;
