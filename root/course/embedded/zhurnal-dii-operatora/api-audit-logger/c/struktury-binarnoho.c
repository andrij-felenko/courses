#pragma pack(push, 1)

/* Структура одного запису аудиту (рівно 128 байтів) */
typedef struct {
    uint32_t magic;                     /* 0..3:   0x41554454 ('AUDT') */
    uint8_t  version;                   /* 4:      Версія формату (0x01) */
    uint8_t  flags;                     /* 5:      Бітова маска audit_flags_t */
    uint8_t  exec_status;               /* 6:      audit_exec_status_t */
    uint8_t  payload_len;               /* 7:      Довжина валідних байтів у payload */
    uint64_t sequence_id;               /* 8..15:  Монотонний лічильник записів */
    uint64_t timestamp_utc_ms;          /* 16..23: Unix Epoch у мілісекундах */
    uint64_t operator_id;               /* 24..31: Ідентифікатор оператора / хеш ключа */
    uint16_t command_id;                /* 32..33: Код команди (MAVLink або custom) */
    uint8_t  subsystem_id;              /* 34:     Цільовий вузол (Autopilot, Gimbal) */
    uint8_t  padding0;                  /* 35:     Вирівнювання */
    uint8_t  payload[AUDIT_MAX_PAYLOAD_SIZE]; /* 36..67: Аргументи команди */
    uint8_t  prev_hash[AUDIT_HASH_SIZE];      /* 68..99: SHA-256 попереднього кадру */
    uint8_t  record_hash[AUDIT_HASH_SIZE];    /* 100..127: SHA-256 поточного кадру */
} audit_record_t;

/* Заголовок 4-кілобайтного сектора Flash */
typedef struct {
    uint32_t sector_magic;              /* 0..3:   0x53454354 ('SECT') */
    uint32_t sector_index;              /* 4..7:   Порядковий номер сектора */
    uint64_t base_sequence_id;          /* 8..15:  Sequence ID першого запису */
    uint8_t  start_hash[AUDIT_HASH_SIZE];/* 16..47: Вхідний хеш ланцюга сектора */
    uint32_t records_count;             /* 48..51: Загальна кількість записів (0xFFFFFFFF якщо пишеться) */
    uint8_t  end_hash[AUDIT_HASH_SIZE]; /* 52..83: Фінальний хеш сектора (при закритті) */
    uint8_t  reserved[44];              /* 84..127: Доповнення до 128 байтів */
} audit_sector_header_t;

#pragma pack(pop)
