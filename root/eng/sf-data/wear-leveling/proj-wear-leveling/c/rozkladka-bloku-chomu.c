#define PAGE_SIZE    2048                 // найменша порція запису
#define PAGES          64                 // сторінок у блоці стирання
#define EC_PAGE         0                 // сторінка з лічильником стирань
#define DATA_PAGE       1                 // перша сторінка даних
#define COMMIT_PAGE  (PAGES - 1)          // коміт — остання сторінка блоку
#define DATA_PAGES   (COMMIT_PAGE - DATA_PAGE)    // 62 сторінки під дані
#define DATA_SIZE    (DATA_PAGES * PAGE_SIZE)     // 126 976 корисних байтів

#define N_PHYS       1024                 // фізичних блоків у чипі (128 МБ)
#define N_LOG         960                 // логічних блоків назовні (~6% у запас)

#define NO_BLOCK     0xFFFFu
#define EC_MAGIC     0x57454331u          // "WEC1"
#define COMMIT_MAGIC 0x57434D31u          // "WCM1"

#define WL_THRESHOLD 4096   // допустимий розкид лічильників — звідки це число, нижче
#define WL_CHECK_EVERY 256  // як часто взагалі перевіряти розкид
#define WL_RESERVE      4   // недоторканний запас вільних блоків

// Заголовок стирання. Пишеться в щойно стертий блок НЕГАЙНО.
typedef struct __attribute__((packed)) {
    uint32_t magic;                       // EC_MAGIC — тут справді заголовок
    uint32_t ec;                          // скільки разів цей блок стирали
    uint8_t  pad[64 - 12];
    uint32_t crc;                         // CRC-32 усього, що вище
} ec_hdr_t;

// Коміт-заголовок. Пишеться ОСТАННІМ і робить блок дійсним.
typedef struct __attribute__((packed)) {
    uint32_t magic;                       // COMMIT_MAGIC
    uint32_t lba;                         // чиї це дані
    uint64_t seq;                         // наскрізний номер запису — суддя при відновленні
    uint32_t data_crc;                    // CRC даних: ловить обірваний запис
    uint8_t  pad[64 - 24];
    uint32_t crc;
} commit_hdr_t;
