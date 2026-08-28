#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VARS 32
#define MAX_FRAMES 16

typedef struct {
    char name[32];
    char value[64];
} Variable;

typedef struct {
    char function_name[32];
    Variable locals[MAX_VARS];
    int local_count;
} CallFrame;

typedef struct {
    CallFrame frames[MAX_FRAMES];
    int frame_top; // 0 - глобальний рівень
} ScopeStack;

void init_scope(ScopeStack *stack) {
    stack->frame_top = 0;
    strcpy(stack->frames[0].function_name, "global");
    stack->frames[0].local_count = 0;
}

void push_frame(ScopeStack *stack, const char *func_name) {
    if (stack->frame_top >= MAX_FRAMES - 1) {
        fprintf(stderr, "Stack overflow!\n");
        return;
    }
    stack->frame_top++;
    strcpy(stack->frames[stack->frame_top].function_name, func_name);
    stack->frames[stack->frame_top].local_count = 0;
    printf("──► Entering function: %s (Depth: %d)\n", func_name, stack->frame_top);
}

void pop_frame(ScopeStack *stack) {
    if (stack->frame_top <= 0) return;
    printf("◄── Exiting function: %s\n", stack->frames[stack->frame_top].function_name);
    stack->frame_top--;
}

void set_local(ScopeStack *stack, const char *name, const char *val) {
    CallFrame *current = &stack->frames[stack->frame_top];
    for (int i = 0; i < current->local_count; i++) {
        if (strcmp(current->locals[i].name, name) == 0) {
            strncpy(current->locals[i].value, val, 63);
            return;
        }
    }
    if (current->local_count < MAX_VARS) {
        strncpy(current->locals[current->local_count].name, name, 31);
        strncpy(current->locals[current->local_count].value, val, 63);
        current->local_count++;
    }
}

// Динамічний пошук: йдемо від вершини стека до глобального фрейму 0
const char* resolve_variable(const ScopeStack *stack, const char *name) {
    for (int f = stack->frame_top; f >= 0; f--) {
        const CallFrame *frame = &stack->frames[f];
        for (int i = 0; i < frame->local_count; i++) {
            if (strcmp(frame->locals[i].name, name) == 0) {
                return frame->locals[i].value;
            }
        }
    }
    return NULL; // Змінна не знайдена
}

void inner_function(ScopeStack *stack) {
    push_frame(stack, "inner_function");
    // inner_function не оголошує 'auth_token', але читає його з контексту виклику!
    const char *token = resolve_variable(stack, "auth_token");
    printf("  [inner_function] Resolved 'auth_token': %s\n", token ? token : "<undefined>");
    pop_frame(stack);
}

void outer_function(ScopeStack *stack) {
    push_frame(stack, "outer_function");
    set_local(stack, "auth_token", "SECRET_KEY_12345");
    inner_function(stack);
    pop_frame(stack);
}

int main(void) {
    ScopeStack stack;
    init_scope(&stack);

    set_local(&stack, "auth_token", "GLOBAL_DEFAULT");
    printf("[Main] Initial auth_token: %s\n", resolve_variable(&stack, "auth_token"));

    outer_function(&stack);

    printf("[Main] auth_token after calls: %s\n", resolve_variable(&stack, "auth_token"));
    return 0;
}
