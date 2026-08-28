int main() {
    georouter::RouterEngine engine;

    georouter::JurisdictionConfig eu_cfg{
        .id = georouter::JurisdictionId::EuEea,
        .name = "European Economic Area",
        .allowed_regions = {"eu-central-1", "eu-west-1"},
        .egress_policy = georouter::EgressPolicy::PermittedPseudonymized,
        .hsm_key_salt = "eu_hsm_salt_secret_2026"
    };
    engine.add_jurisdiction(std::move(eu_cfg));

    georouter::JurisdictionConfig us_cfg{
        .id = georouter::JurisdictionId::UsFed,
        .name = "United States Federal",
        .allowed_regions = {"us-east-1", "us-west-2"},
        .egress_policy = georouter::EgressPolicy::PermittedPseudonymized,
        .hsm_key_salt = "us_kms_salt_secret_2026"
    };
    engine.add_jurisdiction(std::move(us_cfg));

    std::string log_msg;

    // Сценарій 1: Валідний локальний запис
    georouter::TransactionRequest tx1{
        .transaction_id = "tx_1001",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "eu-central-1"
    };

    const auto res1 = engine.process_transaction(tx1, log_msg);
    if (res1.has_value()) {
        std::printf("[Сценарій 1] УСПІХ | %s\n", log_msg.c_str());
        std::printf("              Токен імені: %s | IBAN: %s\n",
                    res1->name_token.c_str(), res1->iban_token.c_str());
    }

    // Сценарій 2: Незаконний транскордонний запис
    georouter::TransactionRequest tx2{
        .transaction_id = "tx_1002",
        .country_code = "DE",
        .tenant_id = "tenant_berlin_fintech",
        .customer_name = "Klaus Mueller",
        .customer_iban = "DE89370400440532013000",
        .amount = 2500.0,
        .target_datacenter = "us-east-1"
    };

    const auto res2 = engine.process_transaction(tx2, log_msg);
    if (!res2.has_value()) {
        std::printf("[Сценарій 2] ВІДХИЛЕНО | %s\n", log_msg.c_str());
    }

    return 0;
}
