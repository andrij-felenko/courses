#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_HEADERS 32
#define MAX_FILTERS 16

/* Типи значень у заголовках повідомлення */
typedef enum {
    VAL_TYPE_STRING,
    VAL_TYPE_INT64,
    VAL_TYPE_DOUBLE,
    VAL_TYPE_BITMASK
} ValueType;

/* Типізоване значення заголовка (Zero-Copy для рядків) */
typedef struct {
    ValueType type;
    union {
        struct {
            const char* ptr;
            size_t len;
        } str;
        int64_t i64;
        double  f64;
        uint64_t mask;
    } as;
} HeaderValue;

/* Окремий заголовок: ключ + значення */
typedef struct {
    const char* key;
    size_t key_len;
    HeaderValue val;
} MessageHeader;

/* Структура повідомлення */
typedef struct {
    uint64_t message_id;
    MessageHeader headers[MAX_HEADERS];
    size_t header_count;
    const uint8_t* payload_ptr;
    size_t payload_len;
} Message;

/* Типи операцій порівняння предикатів */
typedef enum {
    OP_EQUALS_STRING,
    OP_PREFIX_STRING,
    OP_INT_GREATER_THAN,
    OP_INT_LESS_OR_EQUAL,
    OP_BITMASK_ALL_SET,
    OP_HEADER_EXISTS
} PredicateOp;

/* Політика при помилці (відсутнє поле, невідповідний тип) */
typedef enum {
    POLICY_DROP_ON_ERROR,
    POLICY_PASS_ON_ERROR,
    POLICY_DEAD_LETTER_ON_ERROR
} ErrorPolicy;

/* Результат обчислення фільтра */
typedef enum {
    FILTER_DECISION_PASS,
    FILTER_DECISION_DROP,
    FILTER_DECISION_DEAD_LETTER
} FilterDecision;

/* Структура предикату */
typedef struct {
    const char* target_header;
    size_t target_header_len;
    PredicateOp op;
    HeaderValue expected_val;
    bool invert_result; /* Для операції NOT */
} FilterPredicate;

/* Статистика роботи конвеєра */
typedef struct {
    uint64_t total_evaluated;
    uint64_t passed_count;
    uint64_t dropped_count;
    uint64_t dead_letter_count;
} PipelineMetrics;

/* Конвеєр фільтрів (ланцюг) */
typedef struct {
    FilterPredicate predicates[MAX_FILTERS];
    size_t predicate_count;
    ErrorPolicy error_policy;
    PipelineMetrics metrics;
} FilterPipeline;

/* Ініціалізація повідомлення */
void message_init(Message* msg, uint64_t id, const uint8_t* payload, size_t payload_len) {
    msg->message_id = id;
    msg->header_count = 0;
    msg->payload_ptr = payload;
    msg->payload_len = payload_len;
}

/* Додавання рядкового заголовка без копіювання байтів */
bool message_add_str_header(Message* msg, const char* key, const char* str_val) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_STRING;
    h->val.as.str.ptr = str_val;
    h->val.as.str.len = strlen(str_val);
    return true;
}

/* Додавання числового заголовка int64 */
bool message_add_i64_header(Message* msg, const char* key, int64_t val) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_INT64;
    h->val.as.i64 = val;
    return true;
}

/* Додавання бітової маски */
bool message_add_mask_header(Message* msg, const char* key, uint64_t mask) {
    if (msg->header_count >= MAX_HEADERS) return false;
    MessageHeader* h = &msg->headers[msg->header_count++];
    h->key = key;
    h->key_len = strlen(key);
    h->val.type = VAL_TYPE_BITMASK;
    h->val.as.mask = mask;
    return true;
}

/* Пошук заголовка за ключем (O(H)) */
static const HeaderValue* message_find_header(const Message* msg, const char* key, size_t key_len) {
    for (size_t i = 0; i < msg->header_count; ++i) {
        if (msg->headers[i].key_len == key_len &&
            memcmp(msg->headers[i].key, key, key_len) == 0) {
            return &msg->headers[i].val;
        }
    }
    return NULL;
}

/* Ініціалізація конвеєра */
void pipeline_init(FilterPipeline* pipe, ErrorPolicy policy) {
    pipe->predicate_count = 0;
    pipe->error_policy = policy;
    memset(&pipe->metrics, 0, sizeof(PipelineMetrics));
}

/* Додавання предикату до конвеєра */
bool pipeline_add_predicate(FilterPipeline* pipe, FilterPredicate pred) {
    if (pipe->predicate_count >= MAX_FILTERS) return false;
    pipe->predicates[pipe->predicate_count++] = pred;
    return true;
}

/* Оцінка окремого предикату над повідомленням */
static int evaluate_predicate(const FilterPredicate* pred, const Message* msg, bool* out_result) {
    const HeaderValue* actual = message_find_header(msg, pred->target_header, pred->target_header_len);

    if (pred->op == OP_HEADER_EXISTS) {
        *out_result = (actual != NULL) ^ pred->invert_result;
        return 0; /* Успішна оцінка */
    }

    if (!actual) {
        return -1; /* Помилка: заголовок відсутній */
    }

    bool matched = false;
    switch (pred->op) {
        case OP_EQUALS_STRING:
            if (actual->type != VAL_TYPE_STRING) return -1;
            matched = (actual->as.str.len == pred->expected_val.as.str.len) &&
                      (memcmp(actual->as.str.ptr, pred->expected_val.as.str.ptr, actual->as.str.len) == 0);
            break;

        case OP_PREFIX_STRING:
            if (actual->type != VAL_TYPE_STRING) return -1;
            if (actual->as.str.len < pred->expected_val.as.str.len) {
                matched = false;
            } else {
                matched = (memcmp(actual->as.str.ptr, pred->expected_val.as.str.ptr, pred->expected_val.as.str.len) == 0);
            }
            break;

        case OP_INT_GREATER_THAN:
            if (actual->type != VAL_TYPE_INT64) return -1;
            matched = (actual->as.i64 > pred->expected_val.as.i64);
            break;

        case OP_INT_LESS_OR_EQUAL:
            if (actual->type != VAL_TYPE_INT64) return -1;
            matched = (actual->as.i64 <= pred->expected_val.as.i64);
            break;

        case OP_BITMASK_ALL_SET:
            if (actual->type != VAL_TYPE_BITMASK) return -1;
            matched = ((actual->as.mask & pred->expected_val.as.mask) == pred->expected_val.as.mask);
            break;

        default:
            return -1;
    }

    *out_result = matched ^ pred->invert_result;
    return 0;
}

/* Прогін повідомлення крізь конвеєр із short-circuit логікою */
FilterDecision pipeline_process(FilterPipeline* pipe, const Message* msg) {
    pipe->metrics.total_evaluated++;

    for (size_t i = 0; i < pipe->predicate_count; ++i) {
        bool result = false;
        int status = evaluate_predicate(&pipe->predicates[i], msg, &result);

        if (status != 0) {
            /* Обробка ситуації помилки (missing header або type mismatch) */
            switch (pipe->error_policy) {
                case POLICY_DROP_ON_ERROR:
                    pipe->metrics.dropped_count++;
                    return FILTER_DECISION_DROP;
                case POLICY_PASS_ON_ERROR:
                    continue; /* Пропускаємо дефектне правило і йдемо далі */
                case POLICY_DEAD_LETTER_ON_ERROR:
                    pipe->metrics.dead_letter_count++;
                    return FILTER_DECISION_DEAD_LETTER;
            }
        }

        /* Якщо предикат повернув FALSE — негайне скидання (Short-Circuit) */
        if (!result) {
            pipe->metrics.dropped_count++;
            return FILTER_DECISION_DROP;
        }
    }

    pipe->metrics.passed_count++;
    return FILTER_DECISION_PASS;
}

int main(void) {
    FilterPipeline pipeline;
    pipeline_init(&pipeline, POLICY_DROP_ON_ERROR);

    /* Правило 1: Регіон повинен бути "EU" */
    FilterPredicate p1 = {
        .target_header = "region",
        .target_header_len = 6,
        .op = OP_EQUALS_STRING,
        .expected_val = { .type = VAL_TYPE_STRING, .as.str = { .ptr = "EU", .len = 2 } },
        .invert_result = false
    };
    pipeline_add_predicate(&pipeline, p1);

    /* Правило 2: Пріоритет > 3 */
    FilterPredicate p2 = {
        .target_header = "priority",
        .target_header_len = 8,
        .op = OP_INT_GREATER_THAN,
        .expected_val = { .type = VAL_TYPE_INT64, .as.i64 = 3 },
        .invert_result = false
    };
    pipeline_add_predicate(&pipeline, p2);

    /* Тестове повідомлення № 1 (відповідає всім умовам) */
    const char payload1[] = "{\"order_id\": 991, \"amount\": 450.00}";
    Message msg1;
    message_init(&msg1, 1001, (const uint8_t*)payload1, strlen(payload1));
    message_add_str_header(&msg1, "region", "EU");
    message_add_i64_header(&msg1, "priority", 5);

    /* Тестове повідомлення № 2 (чужий регіон "US" -> має бути відкинуте) */
    const char payload2[] = "{\"order_id\": 992, \"amount\": 120.00}";
    Message msg2;
    message_init(&msg2, 1002, (const uint8_t*)payload2, strlen(payload2));
    message_add_str_header(&msg2, "region", "US");
    message_add_i64_header(&msg2, "priority", 9);

    FilterDecision d1 = pipeline_process(&pipeline, &msg1);
    FilterDecision d2 = pipeline_process(&pipeline, &msg2);

    printf("Повідомлення #1001 результат: %s\n", d1 == FILTER_DECISION_PASS ? "PASS" : "DROP");
    printf("Повідомлення #1002 результат: %s\n", d2 == FILTER_DECISION_PASS ? "PASS" : "DROP");
    printf("Метрики конвеєра: всього=%lu, пропущено=%lu, відсіяно=%lu\n",
           pipeline.metrics.total_evaluated,
           pipeline.metrics.passed_count,
           pipeline.metrics.dropped_count);

    return 0;
}
