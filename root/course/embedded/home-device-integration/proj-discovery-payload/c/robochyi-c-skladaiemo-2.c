// Буфери під топік і тіло. Статичні, бо на тісному вузлі не хочемо їх
// на стеку і не хочемо malloc. Розмір — із запасом на найдовшу сутність.
static char topic_buf[128];
static char json_buf[512];

// Скласти й опублікувати візитівку однієї сутності.
// Повертає true, якщо рядок помістився й публікацію віддано в чергу.
static bool announce_entity(const entity_t *e) {
    // 1. Топік опису: homeassistant/<component>/<dev>/<object>/config
    int tn = snprintf(topic_buf, sizeof(topic_buf),
                      "homeassistant/%s/%s/%s/config",
                      e->component, DEV_ID, e->object_id);
    if (tn < 0 || (size_t)tn >= sizeof(topic_buf))
        return false;  // топік не вмістився — не публікуємо покалічене

    // 2. Тіло JSON на СКОРОЧЕНИХ ключах. Одиниці — необовʼязкові, тому
    //    поле unit_of_meas (скор. unit_of_meas → "unit_of_meas") додаємо
    //    лише коли воно є. availability (avty_t) — той самий на всі сутності.
    int n = snprintf(json_buf, sizeof(json_buf),
        "{"
          "\"name\":\"%s\","                 // підпис рядка в картці
          "\"uniq_id\":\"%s_%s\","           // uniq_id = <dev>_<object>, глобально свій
          "\"stat_t\":\"%s\","               // state_topic — де тече значення
          "\"avty_t\":\"" BASE "/status\","  // availability_topic — живий/мертвий
          "%s%s%s"                            // місце під одиниці (або порожньо)
          "\"dev\":{"                          // СПІЛЬНИЙ блок пристрою…
            "\"ids\":\"" DEV_ID "\","          // …той самий ids у всіх сутностей
            "\"name\":\"" DEV_NAME "\","
            "\"mf\":\"DIY\","                  // manufacturer (скор. mf)
            "\"mdl\":\"Thermostat v1\""        // model (скор. mdl)
          "}"
        "}",
        e->name, DEV_ID, e->object_id, e->state_topic,
        e->unit ? "\"unit_of_meas\":\"" : "",   // якщо одиниці є — відкриваємо поле…
        e->unit ? e->unit : "",                  // …значення…
        e->unit ? "\"," : "");                   // …і закриваємо з комою
    if (n < 0 || (size_t)n >= sizeof(json_buf))
        return false;  // JSON зрізало — покалічений опис публікувати НЕ можна

    // 3. Публікуємо: retain=true (щоб HA знайшов пізніше), qos=1 (доставка
    //    напевно; повторний дубль знешкодить uniq_id — оголошення ідемпотентне).
    mqtt_publish(topic_buf, json_buf, (size_t)n, /*qos=*/1, /*retain=*/true);
    return true;
}

// Викликати ОДРАЗУ по під'єднанні до брокера: оголосити всі сутності вузла.
static void announce_all(void) {
    for (size_t i = 0; i < sizeof(ENTITIES) / sizeof(ENTITIES[0]); i++) {
        if (!announce_entity(&ENTITIES[i])) {
            log_error("discovery: сутність %s не вмістилася в буфер",
                      ENTITIES[i].object_id);
        }
    }
}
