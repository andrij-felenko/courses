int main() {
    auto registry = std::make_shared<cqrs::WatermarkRegistry>();
    auto read_store = std::make_shared<cqrs::ReadModelStore>();
    auto write_store = std::make_shared<cqrs::PrimaryWriteStore>();

    cqrs::CausalQueryGateway gateway(registry, read_store, write_store);

    const std::string order_id = "ORD-7714";

    // 1. Командний потік: запис у первинну базу з версією 1042
    cqrs::OrderView fresh_order{order_id, "USER-42", "PAID", 12500, 1042};
    write_store->save(fresh_order);

    // 2. Фоновий потік проєктора: імітація затримки обробки черги (20 мс)
    std::thread projector_thread([&]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        read_store->upsert(fresh_order);
        registry->update_watermark(order_id, 1042);
    });

    // 3. Клієнтський потік: негайний запит із вимогою версії 1042
    auto start_time = std::chrono::steady_clock::now();
    auto result = gateway.get_order(order_id, 1042, std::chrono::milliseconds(100));
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_time
    ).count();

    projector_thread.join();

    if (result.has_value()) {
        std::cout << "[SUCCESS] Отримано замовлення: " << result->order_id 
                  << ", статус: " << result->status 
                  << ", версія: " << result->version 
                  << ", час очікування: " << duration << " мс\n";
    }

    return 0;
}
