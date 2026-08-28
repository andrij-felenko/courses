#include <stdlib.h>
#include <string.h>

DiophContext* dioph_context_create(size_t pool_size) {
    DiophContext* ctx = (DiophContext*)malloc(sizeof(DiophContext));
    if (!ctx) return NULL;
    ctx->memory_pool = (uint8_t*)malloc(pool_size);
    if (!ctx->memory_pool) {
        free(ctx);
        return NULL;
    }
    ctx->pool_size = pool_size;
    ctx->allocated_bytes = 0;
    ctx->var_count = 0;
    ctx->last_error = DIOPH_OK;
    return ctx;
}

void dioph_context_free(DiophContext* ctx) {
    if (!ctx) return;
    free(ctx->memory_pool);
    free(ctx);
}

static void* dioph_arena_alloc(DiophContext* ctx, size_t size) {
    // Вирівнювання на 8 байтів для швидкого доступу процесора
    size_t aligned_size = (size + 7) & ~7;
    if (ctx->allocated_bytes + aligned_size > ctx->pool_size) {
        ctx->last_error = DIOPH_ERR_OUT_OF_MEMORY;
        return NULL;
    }
    void* ptr = ctx->memory_pool + ctx->allocated_bytes;
    ctx->allocated_bytes += aligned_size;
    return ptr;
}

const DiophExpr* dioph_const(DiophContext* ctx, int64_t val) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_CONST;
    e->as.const_val = val;
    return e;
}

const DiophExpr* dioph_var(DiophContext* ctx, const char* name) {
    for (size_t i = 0; i < ctx->var_count; ++i) {
        if (strcmp(ctx->variables[i].name, name) == 0) {
            DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
            if (!e) return NULL;
            e->type = EXPR_VAR;
            e->as.var_id = ctx->variables[i].id;
            return e;
        }
    }
    // Автоматична реєстрація, якщо змінна ще не існує
    if (ctx->var_count >= 128) {
        ctx->last_error = DIOPH_ERR_OUT_OF_MEMORY;
        return NULL;
    }
    uint32_t id = (uint32_t)ctx->var_count;
    strncpy(ctx->variables[id].name, name, 31);
    ctx->variables[id].id = id;
    ctx->variables[id].is_existential = false;
    ctx->var_count++;

    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_VAR;
    e->as.var_id = id;
    return e;
}

const DiophExpr* dioph_add(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_ADD;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophExpr* dioph_sub(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_SUB;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophExpr* dioph_mul(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    DiophExpr* e = (DiophExpr*)dioph_arena_alloc(ctx, sizeof(DiophExpr));
    if (!e) return NULL;
    e->type = EXPR_MUL;
    e->as.binary.lhs = lhs;
    e->as.binary.rhs = rhs;
    return e;
}

const DiophPred* dioph_equal(DiophContext* ctx, const DiophExpr* lhs, const DiophExpr* rhs) {
    const DiophExpr* diff = dioph_sub(ctx, lhs, rhs);
    if (!diff) return NULL;
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_EQUAL_ZERO;
    p->as.eq_zero_expr = diff;
    return p;
}

const DiophPred* dioph_and(DiophContext* ctx, const DiophPred* lhs, const DiophPred* rhs) {
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_AND;
    p->as.binary.lhs = lhs;
    p->as.binary.rhs = rhs;
    return p;
}

const DiophPred* dioph_or(DiophContext* ctx, const DiophPred* lhs, const DiophPred* rhs) {
    DiophPred* p = (DiophPred*)dioph_arena_alloc(ctx, sizeof(DiophPred));
    if (!p) return NULL;
    p->type = PRED_OR;
    p->as.binary.lhs = lhs;
    p->as.binary.rhs = rhs;
    return p;
}
