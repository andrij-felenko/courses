#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t sensor_id;
    double   value;
    uint64_t timestamp;
    bool     is_valid;
} SensorRecord;

// 1. Ітератор джерела: обгортка над сирим масивом
typedef struct {
    const SensorRecord* data;
    size_t count;
    size_t index;
} SourceIterator;

static inline bool source_next(SourceIterator* it, SensorRecord* out) {
    if (it->index < it->count) {
        *out = it->data[it->index++];
        return true;
    }
    return false;
}

// 2. Ітератор фільтрації: пропускає елементи, що не відповідають предикату
typedef bool (*PredicateFn)(const SensorRecord*);

typedef struct {
    SourceIterator* src;
    PredicateFn predicate;
} FilterIterator;

static inline bool filter_next(FilterIterator* it, SensorRecord* out) {
    SensorRecord item;
    while (source_next(it->src, &item)) {
        if (it->predicate(&item)) {
            *out = item;
            return true;
        }
    }
    return false;
}

// 3. Ітератор обмеження (Take): зупиняє потік після N успішних записів
typedef struct {
    FilterIterator* src;
    size_t limit;
    size_t taken;
} TakeIterator;

static inline bool take_next(TakeIterator* it, SensorRecord* out) {
    if (it->taken >= it->limit) return false;
    if (filter_next(it->src, out)) {
        it->taken++;
        return true;
    }
    return false;
}

// Предикат та калібровка як чисті функції
static bool custom_sensor_filter(const SensorRecord* r) {
    return r->is_valid && r->sensor_id == 42 && r->value >= 10.0;
}

static inline double calibrate_transform(double raw_val) {
    return raw_val * 1.08 + 0.5;
}

// Декларативне складання конвеєра
double process_declarative_pipeline(const SensorRecord* records, size_t count, size_t limit) {
    SourceIterator src = { .data = records, .count = count, .index = 0 };
    FilterIterator flt = { .src = &src, .predicate = custom_sensor_filter };
    TakeIterator   tk  = { .src = &flt, .limit = limit, .taken = 0 };

    double sum = 0.0;
    SensorRecord record;
    while (take_next(&tk, &record)) {
        sum += calibrate_transform(record.value);
    }
    return sum;
}
