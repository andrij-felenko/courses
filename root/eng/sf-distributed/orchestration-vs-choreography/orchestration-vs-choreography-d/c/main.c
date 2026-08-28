#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_STEPS 4

typedef enum { STEP_OK = 0, STEP_ERR = 1 } StepResult;

typedef struct {
    char order_id[32];
    double price;
    bool force_logistics_error;
} OrderCtx;

typedef StepResult (*StepFunc)(OrderCtx *ctx);
typedef void (*CompFunc)(OrderCtx *ctx);

typedef struct {
    const char *title;
    StepFunc forward;
    CompFunc compensate;
} StepDef;

/* Прямі дії та компенсації */
StepResult act_inventory(OrderCtx *c) { printf(" [Склад] Резерв товару... [OK]\n"); return STEP_OK; }
void comp_inventory(OrderCtx *c) { printf(" [Склад] ВІДКАТ: Зняття резерву товару.\n"); }

StepResult act_payment(OrderCtx *c) { printf(" [Оплата] Списання %.2f грн... [OK]\n", c->price); return STEP_OK; }
void comp_payment(OrderCtx *c) { printf(" [Оплата] ВІДКАТ: Повернення коштів на карту.\n"); }

StepResult act_logistics(OrderCtx *c) {
    if (c->force_logistics_error) {
        printf(" [Доставка] АВАРІЯ: Немає вільних кур'єрів!\n");
        return STEP_ERR;
    }
    printf(" [Доставка] Кур'єра призначено... [OK]\n");
    return STEP_OK;
}
void comp_logistics(OrderCtx *c) { printf(" [Доставка] ВІДКАТ: Скасування кур'єра.\n"); }

bool run_orchestrator(OrderCtx *ctx) {
    StepDef pipeline[MAX_STEPS] = {
        {"Inventory", act_inventory, comp_inventory},
        {"Payment", act_payment, comp_payment},
        {"Logistics", act_logistics, comp_logistics}
    };
    size_t total_steps = 3;
    CompFunc rollback_stack[MAX_STEPS];
    size_t stack_ptr = 0;

    printf("=== СТАРТ ОРКЕСТРАЦІЇ: %s ===\n", ctx->order_id);
    for (size_t i = 0; i < total_steps; ++i) {
        printf("-> Виконання кроку: %s\n", pipeline[i].title);
        if (pipeline[i].forward(ctx) == STEP_OK) {
            rollback_stack[stack_ptr++] = pipeline[i].compensate;
        } else {
            printf("\n[!] Збій на кроці %s. Оркестратор запускає LIFO відкат:\n", pipeline[i].title);
            while (stack_ptr > 0) {
                rollback_stack[--stack_ptr](ctx);
            }
            printf("=== ПРОЦЕС СКАСОВАНО ТА СТАБІЛІЗОВАНО ===\n");
            return false;
        }
    }
    printf("=== ВСІ КРОКИ УСПІШНО ЗАВЕРШЕНО ===\n");
    return true;
}
