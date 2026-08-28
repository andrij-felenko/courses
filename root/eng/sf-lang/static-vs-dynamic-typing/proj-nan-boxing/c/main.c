#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

/* Базова маска Quiet NaN для 64-бітного слова */
#define QNAN_MASK     ((uint64_t)0x7FF8000000000000ULL)
#define TAG_MASK      ((uint64_t)0x0007000000000000ULL)
#define PAYLOAD_MASK  ((uint64_t)0x0000FFFFFFFFFFFFULL)

/* Теги для типів, що зберігаються всередині NaN */
#define TAG_POINTER   ((uint64_t)0x0001000000000000ULL)
#define TAG_INT       ((uint64_t)0x0002000000000000ULL)
#define TAG_BOOL      ((uint64_t)0x0003000000000000ULL)
#define TAG_NULL      ((uint64_t)0x0004000000000000ULL)

/* Канонічний NaN для представлення дійсного Not-a-Number */
#define CANONICAL_NAN ((uint64_t)0x7FF8000000000000ULL)

typedef uint64_t DynValue;

/* Конструктори значень */
static inline DynValue val_from_double(double num) {
    if (isnan(num)) {
        return CANONICAL_NAN;
    }
    DynValue v;
    memcpy(&v, &num, sizeof(double));
    return v;
}

static inline DynValue val_from_int(int32_t num) {
    return QNAN_MASK | TAG_INT | ((uint64_t)(uint32_t)num);
}

static inline DynValue val_from_bool(bool b) {
    return QNAN_MASK | TAG_BOOL | (b ? 1ULL : 0ULL);
}

static inline DynValue val_from_ptr(void *ptr) {
    return QNAN_MASK | TAG_POINTER | (((uint64_t)ptr) & PAYLOAD_MASK);
}

static inline DynValue val_null(void) {
    return QNAN_MASK | TAG_NULL;
}

/* Предикати перевірки типів */
static inline bool val_is_double(DynValue v) {
    return (v & QNAN_MASK) != QNAN_MASK;
}

static inline bool val_is_int(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_INT);
}

static inline bool val_is_bool(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_BOOL);
}

static inline bool val_is_ptr(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_POINTER);
}

static inline bool val_is_null(DynValue v) {
    return (v & (QNAN_MASK | TAG_MASK)) == (QNAN_MASK | TAG_NULL);
}

/* Розпакування значень */
static inline double val_as_double(DynValue v) {
    double d;
    memcpy(&d, &v, sizeof(double));
    return d;
}

static inline int32_t val_as_int(DynValue v) {
    return (int32_t)(uint32_t)(v & 0xFFFFFFFFULL);
}

static inline bool val_as_bool(DynValue v) {
    return (v & 1ULL) != 0;
}

static inline void* val_as_ptr(DynValue v) {
    return (void*)(uintptr_t)(v & PAYLOAD_MASK);
}

/* Динамічна операція додавання з перевіркою тегів під час виконання */
DynValue dynamic_add(DynValue a, DynValue b, bool *type_error) {
    *type_error = false;

    /* Швидкий шлях: обидва операнди є цілими числами */
    if (val_is_int(a) && val_is_int(b)) {
        return val_from_int(val_as_int(a) + val_as_int(b));
    }

    /* Додавання дійсних чисел (з автоконверсією int -> double) */
    if ((val_is_double(a) || val_is_int(a)) && (val_is_double(b) || val_is_int(b))) {
        double da = val_is_double(a) ? val_as_double(a) : (double)val_as_int(a);
        double db = val_is_double(b) ? val_as_double(b) : (double)val_as_int(b);
        return val_from_double(da + db);
    }

    /* Помилка типізації під час виконання */
    *type_error = true;
    return val_null();
}

int main(void) {
    DynValue v1 = val_from_int(40);
    DynValue v2 = val_from_int(2);
    DynValue v3 = val_from_double(3.14159);
    DynValue v_str_dummy = val_from_ptr((void*)0x7FFF0010);

    bool err = false;
    DynValue res_int = dynamic_add(v1, v2, &err);
    if (!err) {
        printf("Int + Int = %d\n", val_as_int(res_int));
    }

    DynValue res_mixed = dynamic_add(v1, v3, &err);
    if (!err) {
        printf("Int + Double = %f\n", val_as_double(res_mixed));
    }

    DynValue res_invalid = dynamic_add(v1, v_str_dummy, &err);
    if (err) {
        printf("TypeError: несумісні типи операндів під час виконання!\n");
    }

    printf("Розмір DynValue у пам'яті: %zu байтів\n", sizeof(DynValue));
    return 0;
}
