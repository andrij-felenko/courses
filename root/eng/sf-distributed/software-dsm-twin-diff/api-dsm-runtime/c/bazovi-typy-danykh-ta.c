#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define DSM_PAGE_SIZE       4096
#define DSM_MAX_NODES       64
#define DSM_MAX_CHUNKS      128

typedef enum {
    DSM_SUCCESS             =  0,
    DSM_ERR_INVALID_PARAM   = -1,
    DSM_ERR_NO_MEMORY       = -2,
    DSM_ERR_MPROTECT_FAILED = -3,
    DSM_ERR_SIGNAL_FAILED   = -4,
    DSM_ERR_OUT_OF_BOUNDS   = -5,
    DSM_ERR_BUFFER_OVERFLOW = -6
} dsm_status_t;

typedef enum {
    DSM_PAGE_INVALID = 0,   /* PROT_NONE: байти відсутні або застарілі */
    DSM_PAGE_READ_ONLY,     /* PROT_READ: чистий стан, читання без збоїв */
    DSM_PAGE_DIRTY_TWINNED  /* PROT_READ|WRITE: активний двійник, дозволено запис */
} dsm_page_state_t;

/* Заголовок неперервного сегмента відмінностей всередині 4 КБ сторінки */
typedef struct __attribute__((packed)) {
    uint16_t offset;        /* Зсув від початку сторінки (0 .. 4095) */
    uint16_t length;        /* Довжина модифікованого діапазону в байтах (1 .. 4096) */
} dsm_diff_header_t;

/* Структура бінарного пакета різниці сторінки */
typedef struct {
    uint32_t page_id;       /* Глобальний логічний індекс сторінки */
    uint32_t epoch_id;      /* Індекс часового інтервалу / епохи вузла-автора */
    uint16_t chunk_count;   /* Кількість окремих змінених діапазонів */
    uint16_t data_bytes;    /* Сумарний розмір корисних байтів даних */
    uint8_t  payload[DSM_PAGE_SIZE]; /* Буфер заголовків dsm_diff_header_t та сирих даних */
} dsm_diff_packet_t;

/* Конфігурація ініціалізації середовища DSM */
typedef struct {
    size_t   shared_heap_size;   /* Загальний розмір спільного адресного простору в байтах */
    uint32_t node_id;            /* Унікальний ідентифікатор локального вузла (0 .. DSM_MAX_NODES-1) */
    uint32_t total_nodes;        /* Загальна кількість вузлів у кластері */
    bool     enable_simd_diff;   /* Прапорець активації AVX2/AVX-512 прискорення */
} dsm_config_t;
