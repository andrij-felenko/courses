#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Структури для дрібнозернистих відповідей */
typedef struct { char name[64]; char email[64]; } UserProfile;
typedef struct { char city[64]; char street[64]; } UserAddress;
typedef struct { int discount_percent; } UserDiscount;
typedef struct { int order_id; int total_cents; } OrderSummary;

/* Консолідований DTO фасаду */
typedef struct {
    UserProfile profile;
    UserAddress address;
    UserDiscount discount;
    OrderSummary last_order;
    bool is_valid;
} UserDashboardDTO;

/* Імітація дрібнозернистих мережевих функцій (кожна робить RTT) */
bool rpc_get_profile(int user_id, UserProfile* out) {
    if (user_id <= 0) return false;
    snprintf(out->name, sizeof(out->name), "Іван Петренко");
    snprintf(out->email, sizeof(out->email), "ivan@example.com");
    return true;
}

bool rpc_get_address(int user_id, UserAddress* out) {
    if (user_id <= 0) return false;
    snprintf(out->city, sizeof(out->city), "Київ");
    snprintf(out->street, sizeof(out->street), "вул. Хрещатик, 1");
    return true;
}

bool rpc_get_discount(int user_id, UserDiscount* out) {
    if (user_id <= 0) return false;
    out->discount_percent = 15;
    return true;
}

bool rpc_get_last_order(int user_id, OrderSummary* out) {
    if (user_id <= 0) return false;
    out->order_id = 10482;
    out->total_cents = 45000;
    return true;
}

/* 1. Балакучий підхід: 4 послідовні мережеві виклики (4 * RTT) */
bool fetch_dashboard_chatty(int user_id, UserDashboardDTO* out) {
    /* Кожен виклик блокує сокет і очікує підтвердження */
    if (!rpc_get_profile(user_id, &out->profile)) return false;
    if (!rpc_get_address(user_id, &out->address)) return false;
    if (!rpc_get_discount(user_id, &out->discount)) return false;
    if (!rpc_get_last_order(user_id, &out->last_order)) return false;
    out->is_valid = true;
    return true;
}

/* Імітація серверного віддаленого фасаду: 1 мережевий рейс */
bool rpc_facade_get_dashboard(int user_id, UserDashboardDTO* out) {
    /* Сервер виконує всі 4 запити локально в пам'яті (0.01 мс) */
    if (user_id <= 0) return false;
    rpc_get_profile(user_id, &out->profile);
    rpc_get_address(user_id, &out->address);
    rpc_get_discount(user_id, &out->discount);
    rpc_get_last_order(user_id, &out->last_order);
    out->is_valid = true;
    return true;
}

/* 2. Фасадний підхід: 1 грубозернистий мережевий виклик (1 * RTT) */
bool fetch_dashboard_chunky(int user_id, UserDashboardDTO* out) {
    return rpc_facade_get_dashboard(user_id, out);
}
