typedef struct {
    jurisdiction_config_t configs[MAX_JURISDICTIONS];
    size_t count;
} router_engine_t;

void router_init(router_engine_t* engine) {
    engine->count = 0;
}

bool router_add_jurisdiction(router_engine_t* engine, const jurisdiction_config_t* cfg) {
    if (engine->count >= MAX_JURISDICTIONS) return false;
    engine->configs[engine->count++] = *cfg;
    return true;
}

jurisdiction_id_t resolve_jurisdiction(const char* country_code) {
    if (strcmp(country_code, "DE") == 0 || strcmp(country_code, "FR") == 0 ||
        strcmp(country_code, "IT") == 0 || strcmp(country_code, "ES") == 0) {
        return JURISDICTION_EU_EEA;
    }
    if (strcmp(country_code, "US") == 0 || strcmp(country_code, "CA") == 0) {
        return JURISDICTION_US_FED;
    }
    if (strcmp(country_code, "SG") == 0 || strcmp(country_code, "JP") == 0 ||
        strcmp(country_code, "AU") == 0) {
        return JURISDICTION_APAC;
    }
    return JURISDICTION_UNKNOWN;
}

router_status_t route_and_process_transaction(
    const router_engine_t* engine,
    const transaction_request_t* req,
    anonymized_event_t* out_event,
    char* log_buffer,
    size_t log_buf_len
) {
    jurisdiction_id_t j_id = resolve_jurisdiction(req->country_code);
    if (j_id == JURISDICTION_UNKNOWN) {
        snprintf(log_buffer, log_buf_len, "ВІДХИЛЕНО: Невідома юрисдикція для країни %s", req->country_code);
        return ROUTER_ERR_JURISDICTION_UNKNOWN;
    }

    /* Пошук конфігурації юрисдикції */
    const jurisdiction_config_t* cfg = NULL;
    for (size_t i = 0; i < engine->count; i++) {
        if (engine->configs[i].id == j_id) {
            cfg = &engine->configs[i];
            break;
        }
    }
    if (!cfg) return ROUTER_ERR_JURISDICTION_UNKNOWN;

    /* Перевірка дозволених регіонів */
    bool region_allowed = false;
    for (size_t r = 0; r < cfg->region_count; r++) {
        if (strcmp(cfg->allowed_regions[r], req->target_datacenter) == 0) {
            region_allowed = true;
            break;
        }
    }

    if (!region_allowed) {
        snprintf(log_buffer, log_buf_len,
            "БЛОКУВАННЯ GDPR: Спроба передачі даних громадянина %s у несанкціонований регіон %s",
            req->country_code, req->target_datacenter);
        return ROUTER_ERR_CROSS_BORDER_VIOLATION;
    }

    /* Локальна обробка та токенізація для експорту */
    strncpy(out_event->transaction_id, req->transaction_id, sizeof(out_event->transaction_id) - 1);
    out_event->jurisdiction = j_id;
    out_event->amount = req->amount;
    out_event->is_compliant = true;

    generate_deterministic_token(req->customer_name, cfg->hsm_key_salt,
                               out_event->name_token, sizeof(out_event->name_token));
    generate_deterministic_token(req->customer_iban, cfg->hsm_key_salt,
                               out_event->iban_token, sizeof(out_event->iban_token));

    snprintf(log_buffer, log_buf_len,
        "УСПІШНО: Транзакцію %s записано у шард %s (Юрисдикція: %s). Створено токен %s",
        req->transaction_id, req->target_datacenter, cfg->name, out_event->name_token);

    return ROUTER_OK;
}
