#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_STEPS 8
#define MAX_PAYLOAD 128

typedef enum {
    STATUS_SUCCESS = 0,
    STATUS_FAILED = 1
} StepStatus;

typedef struct {
    char order_id[32];
    double amount;
    bool simulate_delivery_failure;
} OrderContext;

/* Сигнатури прямого кроку та компенсаційної дії */
typedef StepStatus (*ForwardAction)(OrderContext *ctx);
typedef void (*CompensateAction)(OrderContext *ctx);

typedef struct {
    const char *name;
    ForwardAction forward;
    CompensateAction compensate;
} SagaStep;

/* ── Доменні функції активностей ── */

StepStatus step_reserve_inventory(OrderContext *ctx) {
    printf("[Склад] Резервування товару для замовлення %s... [УСПІХ]\n", ctx->order_id);
    return STATUS_SUCCESS;
}

void compensate_release_inventory(OrderContext *ctx) {
    printf("[Склад] КОМПЕНСАЦІЯ: Зняття резерву товару для %s.\n", ctx->order_id);
}

StepStatus step_charge_payment(OrderContext *ctx) {
    printf("[Оплата] Списання %.2f грн для замовлення %s... [УСПІХ]\n", ctx->amount, ctx->order_id);
    return STATUS_SUCCESS;
}

void compensate_refund_payment(OrderContext *ctx) {
    printf("[Оплата] КОМПЕНСАЦІЯ: Повернення %.2f грн на картку для %s.\n", ctx->amount, ctx->order_id);
}

StepStatus step_book_delivery(OrderContext *ctx) {
    printf("[Доставка] Спроба призначення кур'єра для %s...\n", ctx->order_id);
    if (ctx->simulate_delivery_failure) {
        printf("[Доставка] ПОМИЛКА: Немає вільних кур'єрів (HTTP 503).\n");
        return STATUS_FAILED;
    }
    printf("[Доставка] Кур'єра призначено успішно.\n");
    return STATUS_SUCCESS;
}

void compensate_cancel_delivery(OrderContext *ctx) {
    printf("[Доставка] КОМПЕНСАЦІЯ: Скасування виклику кур'єра для %s.\n", ctx->order_id);
}

/* ── Рушій оркестрації зі стеком LIFO ── */

typedef struct {
    SagaStep steps[MAX_STEPS];
    size_t step_count;
    CompensateAction rollback_stack[MAX_STEPS];
    size_t stack_top;
} SagaOrchestrator;

void saga_init(SagaOrchestrator *orch) {
    orch->step_count = 0;
    orch->stack_top = 0;
}

void saga_add_step(SagaOrchestrator *orch, const char *name, ForwardAction fwd, CompensateAction comp) {
    if (orch->step_count < MAX_STEPS) {
        orch->steps[orch->step_count].name = name;
        orch->steps[orch->step_count].forward = fwd;
        orch->steps[orch->step_count].compensate = comp;
        orch->step_count++;
    }
}

bool saga_execute(SagaOrchestrator *orch, OrderContext *ctx) {
    printf("\n=== ЗАПУСК ОРКЕСТРАЦІЇ САГИ: %s ===\n", ctx->order_id);
    orch->stack_top = 0;

    for (size_t i = 0; i < orch->step_count; ++i) {
        SagaStep *step = &orch->steps[i];
        printf("-> Оркестратор викликає крок %zu: %s\n", i + 1, step->name);
        
        StepStatus status = step->forward(ctx);
        if (status == STATUS_SUCCESS) {
            /* Якщо крок успішний — реєструємо компенсацію у стеку LIFO */
            if (step->compensate) {
                orch->rollback_stack[orch->stack_top++] = step->compensate;
            }
        } else {
            printf("\n[!] ЗБІЙ на кроці %s. Оркестратор ініціює LIFO відкат!\n", step->name);
            while (orch->stack_top > 0) {
                CompensateAction comp = orch->rollback_stack[--orch->stack_top];
                comp(ctx);
            }
            printf("=== ОРКЕСТРАЦІЮ ЗАВЕРШЕНО З ВІДКАТОМ ===\n");
            return false;
        }
    }

    printf("=== ОРКЕСТРАЦІЮ УСПІШНО ЗАВЕРШЕНО ===\n");
    return true;
}

int main(void) {
    OrderContext ctx = {
        .amount = 45000.0,
        .simulate_delivery_failure = true
    };
    strncpy(ctx.order_id, "ORD-2026-X8", sizeof(ctx.order_id) - 1);

    SagaOrchestrator orch;
    saga_init(&orch);
    saga_add_step(&orch, "ReserveInventory", step_reserve_inventory, compensate_release_inventory);
    saga_add_step(&orch, "ChargePayment", step_charge_payment, compensate_refund_payment);
    saga_add_step(&orch, "BookDelivery", step_book_delivery, compensate_cancel_delivery);

    saga_execute(&orch, &ctx);
    return 0;
}
