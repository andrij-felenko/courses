#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define LWM2M_URI_MAX_DEPTH 4

/* Типи операцій над ресурсом */
typedef enum {
    LWM2M_OP_READ    = 0x01,
    LWM2M_OP_WRITE   = 0x02,
    LWM2M_OP_EXECUTE = 0x04
} lwm2m_operation_t;

/* Типи даних ресурсу */
typedef enum {
    LWM2M_TYPE_STRING,
    LWM2M_TYPE_INTEGER,
    LWM2M_TYPE_FLOAT,
    LWM2M_TYPE_BOOLEAN,
    LWM2M_TYPE_OPAQUE,
    LWM2M_TYPE_EXEC
} lwm2m_data_type_t;

/* Структура опису ресурсу */
typedef struct lwm2m_resource_s {
    uint16_t id;
    uint8_t operations; /* Бітова маска lwm2m_operation_t */
    lwm2m_data_type_t type;
    union {
        int64_t integer;
        float float_val;
        bool boolean;
        const char *string;
        struct {
            const uint8_t *data;
            size_t length;
        } opaque;
        void (*exec_handler)(void);
    } value;
} lwm2m_resource_t;

/* Структура екземпляра об'єкта */
typedef struct lwm2m_instance_s {
    uint16_t instance_id;
    size_t resource_count;
    lwm2m_resource_t *resources;
} lwm2m_instance_t;

/* Структура об'єкта LwM2M */
typedef struct lwm2m_object_s {
    uint16_t object_id;
    size_t instance_count;
    lwm2m_instance_t *instances;
} lwm2m_object_t;

/* Приклад обробника команди перезавантаження */
static void reboot_hardware(void) {
    /* Виклик системного скидання або запуск Watchdog */
}

/* Статична ініціалізація ресурсів Об'єкта 3 (Device) */
static lwm2m_resource_t device_resources[] = {
    {0, LWM2M_OP_READ, LWM2M_TYPE_STRING, {.string = "Acme Corp"}},
    {1, LWM2M_OP_READ, LWM2M_TYPE_STRING, {.string = "FlowMeter-X1"}},
    {4, LWM2M_OP_EXECUTE, LWM2M_TYPE_EXEC, {.exec_handler = reboot_hardware}},
    {9, LWM2M_OP_READ, LWM2M_TYPE_INTEGER, {.integer = 98}}
};

static lwm2m_instance_t device_instances[] = {
    {0, sizeof(device_resources) / sizeof(device_resources[0]), device_resources}
};

/* Статична ініціалізація ресурсів IPSO Об'єкта 3303 (Temperature) */
static lwm2m_resource_t temp_resources[] = {
    {5700, LWM2M_OP_READ, LWM2M_TYPE_FLOAT, {.float_val = 21.5f}},
    {5701, LWM2M_OP_READ, LWM2M_TYPE_STRING, {.string = "Cel"}}
};

static lwm2m_instance_t temp_instances[] = {
    {0, sizeof(temp_resources) / sizeof(temp_resources[0]), temp_resources}
};

/* Реєстр об'єктів клієнта */
static lwm2m_object_t client_registry[] = {
    {3, 1, device_instances},
    {3303, 1, temp_instances}
};

#define REGISTRY_SIZE (sizeof(client_registry) / sizeof(client_registry[0]))

/* Диспетчер запитів CoAP до LwM2M ресурсів */
bool lwm2m_dispatch_read(uint16_t obj_id, uint16_t inst_id, uint16_t res_id, lwm2m_resource_t *out_res) {
    for (size_t o = 0; o < REGISTRY_SIZE; o++) {
        if (client_registry[o].object_id != obj_id) continue;
        for (size_t i = 0; i < client_registry[o].instance_count; i++) {
            if (client_registry[o].instances[i].instance_id != inst_id) continue;
            for (size_t r = 0; r < client_registry[o].instances[i].resource_count; r++) {
                lwm2m_resource_t *res = &client_registry[o].instances[i].resources[r];
                if (res->id == res_id) {
                    if (res->operations & LWM2M_OP_READ) {
                        *out_res = *res;
                        return true;
                    }
                    return false; /* Заборонено для читання */
                }
            }
        }
    }
    return false; /* Не знайдено */
}

bool lwm2m_dispatch_execute(uint16_t obj_id, uint16_t inst_id, uint16_t res_id) {
    for (size_t o = 0; o < REGISTRY_SIZE; o++) {
        if (client_registry[o].object_id != obj_id) continue;
        for (size_t i = 0; i < client_registry[o].instance_count; i++) {
            if (client_registry[o].instances[i].instance_id != inst_id) continue;
            for (size_t r = 0; r < client_registry[o].instances[i].resource_count; r++) {
                lwm2m_resource_t *res = &client_registry[o].instances[i].resources[r];
                if (res->id == res_id) {
                    if ((res->operations & LWM2M_OP_EXECUTE) && res->value.exec_handler) {
                        res->value.exec_handler();
                        return true;
                    }
                    return false;
                }
            }
        }
    }
    return false;
}
