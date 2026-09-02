#ifndef ESC_PROTOCOL_H
#define ESC_PROTOCOL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Кадр телеметрії радіомодема на 57600 бод: одне повідомлення не довше 255 байтів.
   Усе, що не влізло, до оператора не долетить — тому пакувальник рахує байти сам. */
#define ESC_MTU_BYTES      255u
#define ESC_MAX_OPTIONS    4u
#define ESC_DESC_MAX       31u   /* без термінального нуля; UTF-8, тобто ~15 літер */
#define ESC_ROI_MAX        160u  /* стиснений фрагмент кадру, мініатюра 64x64 JPEG */

#define ESC_MAGIC_QUERY    0xE5u
#define ESC_MAGIC_REPLY    0xE6u
#define ESC_WIRE_VERSION   0x01u

/* Прапорці кадру запиту */
#define ESC_FLAG_ROI_DROPPED 0x01u  /* мініатюра не влізла в MTU і викинута */

/* Коди тригерів ескалації — наземна станція за ними підсвічує потрібний шар UI */
typedef enum {
    ESC_TRIGGER_NONE = 0,
    ESC_TRIGGER_SCENE_AMBIGUITY,     /* висока ентропія softmax, класи близькі */
    ESC_TRIGGER_PATH_EXHAUSTED,      /* усі гілки costmap заблоковані */
    ESC_TRIGGER_BORDERLINE_CRITICAL, /* критичний об'єкт у діапазоні [0.4 .. 0.7] */
    ESC_TRIGGER_ODD_EXCURSION        /* вихід за робочий домен (сонце, вітер, EKF) */
} EscTrigger;

/* Дискретна дія, прорахована бортовим планувальником */
typedef struct {
    uint8_t option_id;              /* 1..255, унікальний у межах запиту */
    char    description[ESC_DESC_MAX + 1]; /* підпис кнопки в інтерфейсі оператора */
    float   estimated_cost_detour_m;          /* подовження шляху, метри */
    float   risk_score;             /* залишковий ризик 0.0 .. 1.0 */
} EscOption;

/* Запит до оператора — бортова (розпакована) форма */
typedef struct {
    uint16_t   query_id;            /* монотонний лічильник: захист від фантомного перемикання */
    uint32_t   timestamp_ms;        /* бортовий час створення */
    uint16_t   deadline_ms;         /* динамічний таймаут на відповідь */
    EscTrigger trigger_code;
    uint8_t    flags;
    float      position_xyz[3];
    float      velocity_xyz[3];
    uint8_t    options_count;
    EscOption  options[ESC_MAX_OPTIONS];
    uint16_t   roi_size_bytes;
    uint8_t    roi_jpeg[ESC_ROI_MAX];
} EscQuery;

/* Відповідь оператора */
typedef struct {
    uint16_t query_id;
    uint8_t  option_id;
    uint32_t gcs_time_ms;           /* час станції — лише для журналу інциденту */
} EscReply;

typedef enum {
    ESC_WIRE_OK = 0,
    ESC_WIRE_ERR_SHORT,             /* кадр обірвано */
    ESC_WIRE_ERR_MAGIC,
    ESC_WIRE_ERR_VERSION,
    ESC_WIRE_ERR_CRC,
    ESC_WIRE_ERR_FIELD,             /* поле поза допустимим діапазоном */
    ESC_WIRE_ERR_NO_ROOM            /* не влазить навіть без мініатюри */
} EscWireErr;

uint16_t   esc_crc16(const uint8_t* data, size_t len);
EscWireErr esc_pack_query(const EscQuery* q, uint8_t* out, size_t cap, size_t* written);
EscWireErr esc_unpack_query(const uint8_t* in, size_t len, EscQuery* out);
EscWireErr esc_pack_reply(const EscReply* r, uint8_t* out, size_t cap, size_t* written);
EscWireErr esc_unpack_reply(const uint8_t* in, size_t len, EscReply* out);
const char* esc_wire_err_str(EscWireErr e);

#endif /* ESC_PROTOCOL_H */
