#include <stdio.h>
#include <stdint.h>

/* Трейт Логування: таблиця функцій */
typedef struct LogTraitVTable {
    void (*log_info)(const void *data);
} LogTraitVTable;

/* Жирний покажчик (Fat Pointer) розміром 16 байтів */
typedef struct DynLogger {
    const void *data_ptr;              /* 8 байтів: адреса сирих даних */
    const LogTraitVTable *vtable_ptr;  /* 8 байтів: адреса трейт-таблиці */
} DynLogger;

/* Чиста структура без vptr всередині: розмір рівно 8 байтів */
typedef struct SensorData {
    int32_t temperature;
    int32_t humidity;
} SensorData;

static void sensor_log_impl(const void *data) {
    const SensorData *s = (const SensorData *)data;
    /* У реальній системі тут форматований запис у лог */
    (void)s;
}

static const LogTraitVTable SENSOR_LOG_VTABLE = {
    .log_info = sensor_log_impl
};

/* Створення жирного покажчика на стеку */
static DynLogger make_sensor_logger(const SensorData *s) {
    DynLogger dyn = {
        .data_ptr = s,
        .vtable_ptr = &SENSOR_LOG_VTABLE
    };
    return dyn;
}

/* Приймач жирного покажчика */
static void process_log(DynLogger logger) {
    /* Прямий виклик через передану таблицю без опитування пам'яті об'єкта */
    logger.vtable_ptr->log_info(logger.data_ptr);
}
