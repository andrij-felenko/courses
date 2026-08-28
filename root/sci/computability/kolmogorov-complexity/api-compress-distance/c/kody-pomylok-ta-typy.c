/* ncd_core.h — Коди помилок та типи в C */
typedef enum {
    NCD_SUCCESS             =  0,  /* Успішне виконання */
    NCD_ERR_NULL_POINTER    = -1,  /* Передано NULL-вказівник у критичний аргумент */
    NCD_ERR_EMPTY_BUFFER    = -2,  /* Довжина буфера дорівнює 0 */
    NCD_ERR_ALLOC_FAILED    = -3,  /* Помилка виділення пам'яті під час конкатенації */
    NCD_ERR_COMPRESS_FAIL   = -4,  /* Сбій внутрішнього алгоритму стиснення */
    NCD_ERR_INVALID_ENGINE  = -5   /* Непідтримуваний або недоступний рушій компресії */
} ncd_error_t;

typedef enum {
    NCD_ENGINE_ZLIB  = 0,  /* zlib / Deflate (швидкий, словникове вікно 32 КБ) */
    NCD_ENGINE_BZ2   = 1,  /* bzip2 (перетворення Барроуза-Вілера, вікно 900 КБ) */
    NCD_ENGINE_LZMA  = 2,  /* LZMA / xz (високий коефіцієнт стиснення, вікно до 1 ГБ) */
    NCD_ENGINE_ZSTD  = 3   /* Zstandard (оптимальний баланс швидкості та вікна) */
} ncd_engine_t;

typedef struct {
    ncd_engine_t engine;   /* Обраний алгоритм стиснення */
    int level;             /* Рівень стиснення (від 1 до 9 або від 1 до 22 для zstd) */
    size_t window_size;    /* Розмір словника / вікна в байтах (0 = за замовчуванням) */
    int threads;           /* Кількість паралельних потоків для матричних обчислень */
} ncd_config_t;
