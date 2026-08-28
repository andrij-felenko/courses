#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Нормальна функція перевірки прав */
static int normal_auth(int user_id) {
    printf("[+] Нормальна перевірка: доступ для UID %d обмежено стандартними правами.\n", user_id);
    return 0;
}

/* Привілейована функція (симуляція адміністративного доступу / ROP-гаджета) */
static int root_escalation(int user_id) {
    (void)user_id;
    printf("[!] КРИТИЧНО: Викликано root_escalation! Права підвищено до суперкористувача!\n");
    return 1;
}

/* Структура легітимної сесії (розмір 16 байтів на x86-64) */
typedef struct {
    int (*check_auth)(int);
    int user_id;
    int is_active;
} AuthSession;

/* Структура довільного контенту того самого розмірного класу */
typedef struct {
    uintptr_t raw_field1;
    uintptr_t raw_field2;
} UserComment;

int main(void) {
    printf("=== Симуляція Use-After-Free у мові C ===\n\n");

    /* 1. Виділення первинного об'єкта сесії */
    AuthSession *session = (AuthSession *)malloc(sizeof(AuthSession));
    if (!session) return 1;

    session->user_id = 1000;
    session->is_active = 1;
    session->check_auth = normal_auth;

    printf("[1] Створено сесію за адресою: %p (UID: %d)\n", (void *)session, session->user_id);
    session->check_auth(session->user_id);

    /* 2. Звільнення об'єкта, створення завислого вказівника (Dangling Pointer) */
    printf("\n[2] Виклик free(session) без обнулення вказівника...\n");
    free(session);
    /* session залишається незмінним і все ще вказує на звільнену ділянку пам'яті */

    /* 3. Виділення об'єкта коментаря того самого розміру */
    printf("\n[3] Виділення нового об'єкта UserComment...\n");
    UserComment *comment = (UserComment *)malloc(sizeof(UserComment));
    if (!comment) return 1;

    printf("[3] Новий об'єкт отримав адресу: %p\n", (void *)comment);

    /* Підміна поля check_auth адресою привілейованої функції */
    comment->raw_field1 = (uintptr_t)root_escalation;
    comment->raw_field2 = 0x1337;

    /* 4. Розіменування завислого вказівника (Use-After-Free) */
    printf("\n[4] Виклик session->check_auth() через завислий вказівник...\n");
    session->check_auth(session->user_id);

    free(comment);
    return 0;
}
