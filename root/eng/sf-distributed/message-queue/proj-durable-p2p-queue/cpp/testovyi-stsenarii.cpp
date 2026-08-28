int main() {
    const std::filesystem::path wal_path = "cpp_queue_demo.wal";
    std::filesystem::remove(wal_path);

    std::cout << "=== Старт черги повідомлень Point-to-Point (C++20) ===\n";

    {
        p2p::DurableQueue queue(wal_path);

        std::vector<std::jthread> workers;
        for (int i = 1; i <= 3; ++i) {
            workers.emplace_back([&queue, worker_id = i](std::stop_token st) {
                while (!st.stop_requested()) {
                    auto task = queue.acquire(300ms);
                    if (!task) break;

                    std::cout << "[Воркер C++ " << worker_id << "] Отримав задачу #"
                              << task->id << ": «" << task->payload << "»\n";

                    if (task->id == 2) {
                        std::cout << "[Воркер C++ " << worker_id
                                  << "] ⚡ Імітація зависання на задачі #2 (без ACK)...\n";
                        std::this_thread::sleep_for(600ms);
                        continue;
                    }

                    std::this_thread::sleep_for(50ms);
                    std::cout << "[Воркер C++ " << worker_id << "] Завершив задачу #"
                              << task->id << " -> ACK\n";
                    queue.ack(task->id);
                }
            });
        }

        queue.publish("Транзакція авторизації картки #501");
        queue.publish("Формування рахунку-фактури #502");
        queue.publish("Перевірка балансу #503");
        queue.publish("Оновлення бонусного рахунку #504");

        std::this_thread::sleep_for(1200ms);
        queue.stop();
    }

    std::cout << "=== Демонстрацію завершено. Журнал перевірено ===\n";
    std::filesystem::remove(wal_path);
    return 0;
}
