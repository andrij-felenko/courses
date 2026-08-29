/* Метадані збірки, вкладені в саму прошивку.
   Лежать у секції .meta одразу за таблицею векторів — за фіксованим і
   наперед відомим зсувом, тож бутлоадер або сервісна утиліта читають їх
   з голого двійкового образу, не розбираючи ELF. */
#ifndef BUILD_META_H
#define BUILD_META_H

#include <stddef.h>
#include <stdint.h>

#define FW_META_MAGIC   0x544F4F4CU /* 'TOOL' у порядку little-endian */
#define FW_META_VERSION 1U
#define FW_META_SIZE    92U         /* мусить збігатися з LAYOUT у stamp_meta.py */

/* Пакована: розкладку читають ззовні (Python, бутлоадер), тож жодних
   вирівнювальних дірок, які компілятор має право вставити сам. */
typedef struct {
    uint32_t magic;             /* FW_META_MAGIC */
    uint16_t version;           /* FW_META_VERSION */
    uint16_t size;              /* sizeof(fw_meta_t) — захист від розбіжних версій */
    uint32_t build_epoch;       /* SOURCE_DATE_EPOCH, а не час компіляції */
    uint32_t image_size;        /* довжина firmware.bin; 0 = ще не проштамповано */
    uint32_t image_crc32;       /* CRC32 образу з обнуленим цим самим полем */
    char     git_commit[40];    /* повний SHA-1 у hex, без нульового байта */
    char     toolchain_id[32];  /* «gcc-13.2-<перші 12 символів хешу архіву>» */
} __attribute__((packed)) fw_meta_t;

typedef enum {
    FW_META_OK = 0,
    FW_META_ERR_ARG,        /* NULL замість образу чи метаданих */
    FW_META_ERR_MAGIC,      /* сигнатури немає — це не наш образ */
    FW_META_ERR_VERSION,    /* формат новіший або старіший за відомий коду */
    FW_META_ERR_SIZE,       /* структура іншої довжини: несумісний штампувальник */
    FW_META_ERR_UNSTAMPED,  /* образ зібрано, але stamp_meta.py по ньому не пройшов */
    FW_META_ERR_RANGE,      /* метадані лежать поза межами наданого образу */
    FW_META_ERR_CRC         /* образ пошкоджено або підмінено */
} fw_meta_status_t;

/* Екземпляр у секції .meta: заповнюється значеннями, що їх Makefile
   передав через -D, і доштамповується після компонування. */
extern const fw_meta_t fw_meta;

/* Ті самі метадані, але прочитані з Flash за адресою секції.
   Саме цим викликом користуються всі перевірки: до звичайного `fw_meta`
   компілятор має повне право підставити нулі, які лежали в екземплярі
   ДО штампування, — і перевірка CRC мовчки виродилася б у константу. */
const fw_meta_t *fw_meta_current(void);

/* Повна перевірка: сигнатура, версія, довжина, межі й CRC32 усього образу.
   image/image_len — фактичні межі прошитого двійкового образу. */
fw_meta_status_t fw_meta_verify(const fw_meta_t *meta,
                                const uint8_t *image,
                                uint32_t image_len);

/* Короткий текстовий опис статусу для журналу чи діагностичної скриньки. */
const char *fw_meta_status_text(fw_meta_status_t status);

/* Однорядковий звіт «чим і коли це зібрано» у наданий буфер, без stdio.
   Повертає кількість записаних байтів (без нульового), обрізаючи по cap. */
size_t fw_meta_report(char *buf, size_t cap, const fw_meta_t *meta);

#endif /* BUILD_META_H */
