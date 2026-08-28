int main() {
    std::cout << "=== Демонстрація роботи каркаса SASL (C++) ===\n";

    // 1. Налаштування облікових даних
    SaslCredentials creds{
        .authzid = std::nullopt,
        .authcid = "alice",
        .password = "SecretPass_42!"
    };

    auto plain_mech = std::make_shared<SaslPlainMechanism>();
    SaslClientSession client(plain_mech, creds);

    // 2. Клієнт генерує початкову відповідь
    SecureByteVector client_output;
    auto status = client.process({}, client_output);

    if (status == SaslStatus::Ok) {
        std::cout << "[Клієнт] Згенеровано Initial Response, розмір: " << client_output.size() << " байтів\n";
    }

    // 3. Сервер обробляє отримані байти
    std::string auth_user;
    SecureByteVector server_output;
    auto s_status = plain_mech->server_step(client_output.span(), server_output, auth_user);

    if (s_status == SaslStatus::Ok) {
        std::cout << "[Сервер] Успіх! Авторизовано користувача: " << auth_user << "\n";
    } else {
        std::cout << "[Сервер] Відмова в автентифікації!\n";
    }

    return 0;
}
