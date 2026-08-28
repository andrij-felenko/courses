int main(void) {
    router_engine_t engine;
    router_init(&engine);

    /* Налаштування юрисдикції ЄС */
    jurisdiction_config_t eu_cfg = {
        .id = JURISDICTION_EU_EEA,
        .name = "European Economic Area",
        .region_count = 2,
        .egress_policy = EGRESS_PERMITTED_PSEUDONYMIZED,
        .hsm_key_salt = "eu_hsm_salt_secret_2026"
    };
    strncpy(eu_cfg.allowed_regions[0], "eu-central-1", MAX_NAME_LEN);
    strncpy(eu_cfg.allowed_regions[1], "eu-west-1", MAX_NAME_LEN);
    router_add_jurisdiction(&engine, &eu_cfg);

    /* Налаштування юрисдикції США */
    jurisdiction_config_t us_cfg = {
        .id = JURISDICTION_US_FED,
        .name = "United States Federal",
        .region_count = 2,
        .egress_policy = EGRESS_PERMITTED_PSEUDONYMIZED,
        .hsm_key_salt = "us_kms_salt_secret_2026"
    };
    strncpy(us_cfg.allowed_regions[0], "us-east-1", MAX_NAME_LEN);
    strncpy(us_cfg.allowed_regions[1], "us-west-2", MAX_NAME_LEN);
    router_add_jurisdiction(&engine, &us_cfg);

    char log_buf[256];
    anonymized_event_t event;

    /* Сценарій 1: Валідний локальний запис у межах ЄС */
    transaction_request_t tx1 = {
        .transaction_id = "tx_1001",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "eu-central-1"
    };

    router_status_t status1 = route_and_process_transaction(&engine, &tx1, &event, log_buf, sizeof(log_buf));
    printf("[Сценарій 1] Статус: %d | Лог: %s\n", status1, log_buf);
    if (status1 == ROUTER_OK) {
        printf("              Псевдонім імені: %s | IBAN токен: %s\n", event.name_token, event.iban_token);
    }

    /* Сценарій 2: Спроба незаконного транскордонного запису */
    transaction_request_t tx2 = {
        .transaction_id = "tx_1002",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "us-east-1"  /* Порушення: сервер у США */
    };

    router_status_t status2 = route_and_process_transaction(&engine, &tx2, &event, log_buf, sizeof(log_buf));
    printf("[Сценарій 2] Статус: %d | Лог: %s\n", status2, log_buf);

    return 0;
}
