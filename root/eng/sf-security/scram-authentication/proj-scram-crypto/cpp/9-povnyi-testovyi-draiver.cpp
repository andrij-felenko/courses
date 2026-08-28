/* Тестовий драйвер для C++20 */
[[nodiscard]] bool run_scram_validation_suite() {
    using namespace scram;

    constexpr std::string_view password = "pencil";
    constexpr std::array<uint8_t, 12> salt = {
        0x41, 0x25, 0xc2, 0x47, 0xe4, 0x3a, 0xb1, 0xe9, 0x3c, 0x6d, 0xff, 0x76
    };
    constexpr int iterations = 4096;
    constexpr std::string_view auth_message =
        "n=user,r=fyko+d2lbbFgONRv9qkxdawL,"
        "r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j,s=QSXCR+Q6sek8bf92,"
        "i=4096,c=biws,r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j";

    constexpr byte_block expected_proof = {
        0x8d, 0xa6, 0x49, 0xbf, 0x70, 0x73, 0xd9, 0x3d,
        0x02, 0x24, 0x66, 0xc9, 0x43, 0x01, 0x74, 0x5f,
        0xe1, 0xc8, 0xa2, 0x2a, 0x6f, 0x7f, 0x40, 0x65,
        0x66, 0x83, 0xaa, 0x83, 0x6a, 0x34, 0xe5, 0x55
    };

    try {
        byte_block salted = scram_service::derive_salted_password(password, salt, iterations);
        auto creds = scram_service::derive_credentials(salted);

        byte_block proof = scram_service::compute_client_proof(
            creds.client_key, creds.stored_key, auth_message);

        if (proof != expected_proof) {
            return false;
        }

        byte_block server_sig{};
        if (!scram_service::server_authenticate(
                creds.stored_key, creds.server_key, proof, auth_message, server_sig)) {
            return false;
        }

        return scram_service::client_verify_server(creds.server_key, auth_message, server_sig);
    } catch (const std::exception&) {
        return false;
    }
}
