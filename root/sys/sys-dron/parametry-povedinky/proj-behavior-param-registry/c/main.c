#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_PARAMS 32
#define FLASH_SECTOR_SIZE 512
#define MAGIC_HEADER 0x5041524DU // "PARM"

// Таблиця швидкого розрахунку CRC32 (IEEE 802.3, поліном 0xEDB88320)
static const uint32_t crc32_tab[16] = {
    0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
    0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
    0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
    0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
};

uint32_t calculate_crc32(const uint8_t* data, size_t length) {
    uint32_t crc = ~0U;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        crc = (crc >> 4) ^ crc32_tab[crc & 0x0F];
        crc = (crc >> 4) ^ crc32_tab[crc & 0x0F];
    }
    return ~crc;
}

// Типи параметрів за стандартом MAVLink (MAV_PARAM_TYPE)
typedef enum {
    MAV_PARAM_TYPE_INT32  = 6,
    MAV_PARAM_TYPE_REAL32 = 9
} mav_param_type_t;

typedef enum {
    PARAM_FLAG_NONE          = 0,
    PARAM_FLAG_DISARMED_ONLY = 1 << 0,
    PARAM_FLAG_REBOOT_REQ    = 1 << 1,
    PARAM_FLAG_READ_ONLY     = 1 << 2
} param_flags_t;

typedef union {
    int32_t i32;
    float   f32;
    uint8_t raw[4];
} param_val_t;

typedef struct {
    char             name[16];
    mav_param_type_t type;
    param_val_t      min_val;
    param_val_t      max_val;
    param_val_t      def_val;
    uint16_t         flags;
} param_meta_t;

typedef struct {
    const param_meta_t* meta;
    param_val_t         val;
    volatile bool       dirty;
} param_record_t;

// Структура сектора збереження у Flash (фіксоване вирівнювання за 4 байтами)
typedef struct {
    uint32_t    magic;
    uint32_t    seq_num;
    uint16_t    count;
    uint16_t    reserved;
    param_val_t values[MAX_PARAMS];
    uint32_t    crc32;
} __attribute__((packed)) flash_sector_t;

// Глобальний реєстр параметрів
typedef struct {
    param_record_t records[MAX_PARAMS];
    size_t         count;
    uint32_t       current_seq;
    uint8_t        active_sector;
    uint8_t        flash_storage[2][FLASH_SECTOR_SIZE]; // Сектори 0 та 1
} param_registry_t;

static param_registry_t g_registry;

// Реєстрація дескриптора параметра під час завантаження системи
int param_register(const param_meta_t* meta) {
    if (!meta || g_registry.count >= MAX_PARAMS) return -1;
    size_t idx = g_registry.count++;
    g_registry.records[idx].meta = meta;
    g_registry.records[idx].val = meta->def_val;
    g_registry.records[idx].dirty = false;
    return (int)idx;
}

// Пряме детерміноване читання для контурів стабілізації (O(1))
bool param_get_fast(int handle, param_val_t* out_val) {
    if (handle < 0 || (size_t)handle >= g_registry.count || !out_val) return false;
    *out_val = g_registry.records[handle].val;
    return true;
}

// Пошук числового дескриптора за рядковим іменем (для MAVLink-обробника)
int param_find(const char* name) {
    if (!name) return -1;
    for (size_t i = 0; i < g_registry.count; ++i) {
        if (strncmp(g_registry.records[i].meta->name, name, 16) == 0) {
            return (int)i;
        }
    }
    return -1;
}

// Валідація значень та запис у кеш ОЗП
bool param_set_value(int handle, param_val_t new_val, bool is_armed) {
    if (handle < 0 || (size_t)handle >= g_registry.count) return false;
    param_record_t* rec = &g_registry.records[handle];
    const param_meta_t* meta = rec->meta;

    // Перевірка атрибута тільки для читання
    if (meta->flags & PARAM_FLAG_READ_ONLY) {
        return false;
    }

    // Перевірка блокування змін при зведених моторах
    if (is_armed && (meta->flags & PARAM_FLAG_DISARMED_ONLY)) {
        return false;
    }

    // Синтаксична перевірка діапазонів
    if (meta->type == MAV_PARAM_TYPE_REAL32) {
        if (new_val.f32 < meta->min_val.f32 || new_val.f32 > meta->max_val.f32) {
            return false;
        }
    } else if (meta->type == MAV_PARAM_TYPE_INT32) {
        if (new_val.i32 < meta->min_val.i32 || new_val.i32 > meta->max_val.i32) {
            return false;
        }
    }

    rec->val = new_val;
    rec->dirty = true;
    return true;
}

// Двобуферне збереження у Flash із розрахунком CRC32
bool param_save_to_flash(void) {
    uint8_t next_sector = (g_registry.active_sector == 0) ? 1 : 0;
    flash_sector_t sec;
    memset(&sec, 0, sizeof(sec));

    sec.magic = MAGIC_HEADER;
    sec.seq_num = g_registry.current_seq + 1;
    sec.count = (uint16_t)g_registry.count;

    for (size_t i = 0; i < g_registry.count; ++i) {
        sec.values[i] = g_registry.records[i].val;
    }

    // Розрахунок CRC32 для всього тіла без поля crc32
    size_t payload_size = sizeof(flash_sector_t) - sizeof(uint32_t);
    sec.crc32 = calculate_crc32((const uint8_t*)&sec, payload_size);

    // Запис у неактивний сектор
    memcpy(&g_registry.flash_storage[next_sector][0], &sec, sizeof(sec));

    // Верифікація записаного образу
    const flash_sector_t* written = (const flash_sector_t*)&g_registry.flash_storage[next_sector][0];
    uint32_t verify_crc = calculate_crc32((const uint8_t*)written, payload_size);

    if (verify_crc == written->crc32) {
        g_registry.active_sector = next_sector;
        g_registry.current_seq = sec.seq_num;
        for (size_t i = 0; i < g_registry.count; ++i) {
            g_registry.records[i].dirty = false;
        }
        return true;
    }
    return false;
}

// Завантаження параметрів під час старту з відновленням після аварій
bool param_load_from_flash(void) {
    bool sector_valid[2] = {false, false};
    flash_sector_t sec[2];
    size_t payload_size = sizeof(flash_sector_t) - sizeof(uint32_t);

    for (int i = 0; i < 2; ++i) {
        memcpy(&sec[i], &g_registry.flash_storage[i][0], sizeof(flash_sector_t));
        if (sec[i].magic == MAGIC_HEADER) {
            uint32_t crc = calculate_crc32((const uint8_t*)&sec[i], payload_size);
            if (crc == sec[i].crc32) {
                sector_valid[i] = true;
            }
        }
    }

    int best_sector = -1;
    if (sector_valid[0] && sector_valid[1]) {
        best_sector = (sec[0].seq_num >= sec[1].seq_num) ? 0 : 1;
    } else if (sector_valid[0]) {
        best_sector = 0;
    } else if (sector_valid[1]) {
        best_sector = 1;
    }

    if (best_sector < 0) {
        // Обидва сектори пошкоджені: завантаження дефолтних значень
        for (size_t i = 0; i < g_registry.count; ++i) {
            g_registry.records[i].val = g_registry.records[i].meta->def_val;
            g_registry.records[i].dirty = false;
        }
        return false;
    }

    g_registry.active_sector = (uint8_t)best_sector;
    g_registry.current_seq = sec[best_sector].seq_num;

    size_t load_count = (g_registry.count < sec[best_sector].count) ? 
                        g_registry.count : sec[best_sector].count;

    for (size_t i = 0; i < load_count; ++i) {
        g_registry.records[i].val = sec[best_sector].values[i];
        g_registry.records[i].dirty = false;
    }
    return true;
}

// Структури повідомлень протоколу MAVLink
typedef struct {
    float   param_value;
    uint8_t target_system;
    uint8_t target_component;
    char    param_id[16];
    uint8_t param_type;
} mavlink_param_set_t;

typedef struct {
    float    param_value;
    uint16_t param_count;
    uint16_t param_index;
    char     param_id[16];
    uint8_t  param_type;
} mavlink_param_value_t;

// Обробник вхідного повідомлення PARAM_SET із квитуванням PARAM_VALUE
bool mavlink_handle_param_set(const mavlink_param_set_t* set_msg, 
                              mavlink_param_value_t* out_val_msg, 
                              bool is_armed) {
    if (!set_msg || !out_val_msg) return false;

    int handle = param_find(set_msg->param_id);
    if (handle < 0) return false;

    const param_record_t* rec = &g_registry.records[handle];
    param_val_t incoming;

    // Побітове перетворення wire float у внутрішнє представлення
    if (rec->meta->type == MAV_PARAM_TYPE_REAL32) {
        incoming.f32 = set_msg->param_value;
    } else {
        memcpy(&incoming.i32, &set_msg->param_value, sizeof(int32_t));
    }

    bool updated = param_set_value(handle, incoming, is_armed);

    // Підготовка відповіді PARAM_VALUE
    memset(out_val_msg, 0, sizeof(*out_val_msg));
    memcpy(out_val_msg->param_id, rec->meta->name, 16);
    out_val_msg->param_type = (uint8_t)rec->meta->type;
    out_val_msg->param_count = (uint16_t)g_registry.count;
    out_val_msg->param_index = (uint16_t)handle;

    if (rec->meta->type == MAV_PARAM_TYPE_REAL32) {
        out_val_msg->param_value = rec->val.f32;
    } else {
        memcpy(&out_val_msg->param_value, &rec->val.i32, sizeof(float));
    }

    if (updated) {
        param_save_to_flash();
    }

    return updated;
}
