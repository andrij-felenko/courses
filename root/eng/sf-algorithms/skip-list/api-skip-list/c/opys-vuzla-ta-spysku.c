/* Визначення констант конфігурації */
#define SKIPLIST_MAX_LEVEL 32
#define SKIPLIST_P_FACTOR 4  /* p = 1/4 */

/* Коди помилок операцій */
typedef enum {
    SKIPLIST_OK = 0,
    SKIPLIST_ERR_NOMEM = -1,
    SKIPLIST_ERR_NOTFOUND = -2,
    SKIPLIST_ERR_EXISTS = -3,
    SKIPLIST_ERR_INVALID = -4
} SkipListStatus;

/* Структура діагностичної статистики */
typedef struct SkipListStats {
    size_t total_nodes;          /* Загальна кількість вузлів */
    size_t current_max_level;    /* Поточний найвищий рівень */
    size_t total_memory_bytes;   /* Сумарна зайнята пам'ять у байтах */
    double avg_pointers_per_node;/* Середня кількість покажчиків на вузол */
    size_t level_counts[SKIPLIST_MAX_LEVEL]; /* Розподіл вузлів за рівнями */
} SkipListStats;

/* Структура вузла з гнучким масивом покажчиків */
typedef struct SkipNode {
    int key;                     /* Ключ елемента */
    int value;                   /* Корисне навантаження */
    int level;                   /* Висота вежі покажчиків даного вузла */
    struct SkipNode* forward[];  /* Масив покажчиків forward[0...level-1] */
} SkipNode;

/* Головний дескриптор пропускного списку */
typedef struct SkipList {
    int level;                   /* Поточний найвищий активний рівень */
    size_t size;                 /* Кількість збережених пар ключ-значення */
    SkipNode* head;              /* Вказівник на вартовий вузол */
} SkipList;
