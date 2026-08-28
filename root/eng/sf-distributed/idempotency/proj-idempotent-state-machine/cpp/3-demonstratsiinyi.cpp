int main() {
    IdempotencyEngine engine(std::chrono::seconds(10), std::chrono::seconds(3600));

    constexpr std::string_view key = "req-uuid-9948-2831";
    constexpr std::string_view orderPayload = R"({"order_id": 101, "amount": 500})";
    constexpr std::string_view tamperedPayload = R"({"order_id": 101, "amount": 9999})";

    // Сценарій 1: Первинний запит
    auto res1 = engine.acquireOrCheck(key, orderPayload);
    if (res1.has_value() && !res1.value().has_value()) {
        std::cout << "[Спроба 1] EXECUTE -> проводимо транзакцію\n";
        engine.commit(key, 200, R"({"status": "PAID", "tx_id": 98871})");
    }

    // Сценарій 2: Повторний виклик через втрату мережевого підтвердження
    auto res2 = engine.acquireOrCheck(key, orderPayload);
    if (res2.has_value() && res2.value().has_value()) {
        const auto& cached = res2.value().value();
        std::cout << "[Спроба 2] RETURN_CACHED -> код " << cached.statusCode 
                  << ", тіло: " << cached.body << "\n";
    }

    // Сценарій 3: Спроба підміни суми платежу під тим самим ключем
    auto res3 = engine.acquireOrCheck(key, tamperedPayload);
    if (!res3.has_value() && res3.error() == IdemError::PayloadMismatch) {
        std::cout << "[Спроба 3] PAYLOAD_MISMATCH -> операцію заблоковано (422 Unprocessable)\n";
    }

    return 0;
}
