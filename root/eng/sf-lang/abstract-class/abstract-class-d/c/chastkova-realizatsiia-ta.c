#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

typedef struct DataPipeline DataPipeline;

typedef struct DataPipelineVTable {
    void (*parse_and_transform)(DataPipeline* self, const char* payload);
    bool (*should_audit)(const DataPipeline* self);
} DataPipelineVTable;

struct DataPipeline {
    const DataPipelineVTable* vptr;
};

/* Невіртуальний каркас NVI мовою C */
void data_pipeline_execute(DataPipeline* self, const char* payload) {
    printf(">>> Початок обробки транзакції\n");
    if (!payload || strlen(payload) == 0) {
        fprintf(stderr, "Помилка: порожні дані\n");
        return;
    }

    /* Виклик обов'язкового кроку нащадка */
    self->vptr->parse_and_transform(self, payload);

    /* Виклик опціонального гачка */
    if (self->vptr->should_audit(self)) {
        printf("[AUDIT]: Запис успішно збережено в журнал\n");
    }
    printf("<<< Завершено\n");
}

/* Конкретний нащадок мовою C */
typedef struct JsonPipeline {
    DataPipeline base;
} JsonPipeline;

static void json_parse_impl(DataPipeline* self, const char* payload) {
    (void)self;
    printf("  Парсинг JSON-дерева: %s\n", payload);
}

static bool json_audit_impl(const DataPipeline* self) {
    (void)self;
    return false;
}

static const DataPipelineVTable g_json_vtable = {
    .parse_and_transform = json_parse_impl,
    .should_audit = json_audit_impl
};

void json_pipeline_init(JsonPipeline* pipeline) {
    pipeline->base.vptr = &g_json_vtable;
}
