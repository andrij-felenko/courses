#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_BINDINGS 64

typedef struct {
    char name[32];
    int value;
} Binding;

typedef struct Environment {
    Binding bindings[MAX_BINDINGS];
    size_t count;
    struct Environment* parent;
    size_t ref_count; // Лічильник посилань для підтримки замикань
} Environment;

// Створення нового кадру оточення
Environment* env_create(Environment* parent) {
    Environment* env = (Environment*)malloc(sizeof(Environment));
    if (!env) return NULL;
    env->count = 0;
    env->parent = parent;
    env->ref_count = 1;
    if (parent) {
        parent->ref_count++;
    }
    return env;
}

// Звільнення пам'яті з урахуванням замикань та каскадного видалення предків
void env_release(Environment* env) {
    if (!env) return;
    env->ref_count--;
    if (env->ref_count == 0) {
        Environment* p = env->parent;
        free(env);
        if (p) {
            env_release(p);
        }
    }
}

// Оголошення змінної в поточному блоці (затінює однойменні зовнішні)
bool env_define(Environment* env, const char* name, int value) {
    for (size_t i = 0; i < env->count; ++i) {
        if (strcmp(env->bindings[i].name, name) == 0) {
            env->bindings[i].value = value;
            return true;
        }
    }
    if (env->count >= MAX_BINDINGS) return false;
    strncpy(env->bindings[env->count].name, name, 31);
    env->bindings[env->count].name[31] = '\0';
    env->bindings[env->count].value = value;
    env->count++;
    return true;
}

// Лексичний пошук ідентифікатора вгору по дереву
bool env_lookup(const Environment* env, const char* name, int* out_val) {
    const Environment* curr = env;
    while (curr != NULL) {
        for (size_t i = 0; i < curr->count; ++i) {
            if (strcmp(curr->bindings[i].name, name) == 0) {
                *out_val = curr->bindings[i].value;
                return true;
            }
        }
        curr = curr->parent; // крок до лексичного предка
    }
    return false;
}

// Зміна значення існуючої змінної у найближчому видимому кадрі
bool env_assign(Environment* env, const char* name, int value) {
    Environment* curr = env;
    while (curr != NULL) {
        for (size_t i = 0; i < curr->count; ++i) {
            if (strcmp(curr->bindings[i].name, name) == 0) {
                curr->bindings[i].value = value;
                return true;
            }
        }
        curr = curr->parent;
    }
    return false;
}

int main(void) {
    // 1. Створення глобального оточення
    Environment* global_env = env_create(NULL);
    env_define(global_env, "x", 10);
    env_define(global_env, "g_flag", 1);

    // 2. Вхід у блок функції: створюємо дочірній кадр
    Environment* func_env = env_create(global_env);
    env_define(func_env, "x", 20); // Затінення global 'x'

    // 3. Вхід у вкладений блок (наприклад, тіло if)
    Environment* block_env = env_create(func_env);
    env_define(block_env, "y", 30);

    int val = 0;
    // Блок бачить локальний затінений x = 20
    env_lookup(block_env, "x", &val);
    printf("Block sees x = %d (expected 20)\n", val);

    // Блок бачить глобальний g_flag = 1 через ланцюжок предків
    env_lookup(block_env, "g_flag", &val);
    printf("Block sees g_flag = %d (expected 1)\n", val);

    // Мутація глобальної змінної з вкладеного блоку
    env_assign(block_env, "g_flag", 99);
    env_lookup(global_env, "g_flag", &val);
    printf("Global g_flag after assign = %d (expected 99)\n", val);

    // Вихід із блоків та коректне звільнення пам'яті
    env_release(block_env);
    env_release(func_env);
    env_release(global_env);
    return 0;
}
