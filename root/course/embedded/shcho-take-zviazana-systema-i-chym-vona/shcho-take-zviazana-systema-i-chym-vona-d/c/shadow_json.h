#ifndef SHADOW_JSON_H
#define SHADOW_JSON_H

#include <stddef.h>

#include "state_manager.h"

/*
 * Мінімальний розбір і складання документів тіні пристрою.
 * Дельта — плаский об'єкт без вкладень і масивів, саме так її шле брокер:
 *   {"version":9,"temp":24.5,"fan":2400,"heat":true}
 * Тут перевіряємо ЛИШЕ синтаксис і типи; фізичні межі судить агент стану.
 */

/* Повертає кількість розібраних полів (0..3) або -1 на покрученому документі
   чи документі без обов'язкової версії. */
int shadow_json_parse_delta(const char *doc, size_t len, shadow_delta_t *out);

/* Складає payload для топіка .../shadow/update. Повертає довжину або -1,
   якщо буфер замалий: обрізаний JSON у канал не пускаємо. */
int shadow_json_build_reported(const state_agent_t *agent, char *buf, size_t cap);

#endif /* SHADOW_JSON_H */
