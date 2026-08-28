#include <iostream>
#include <cassert>
#include <string>

// Некопійований тип даних для перевірки коректності семантики переміщення
struct SensorPayload {
    int sensor_id{0};
    std::string data;

    SensorPayload(int id, std::string d) : sensor_id(id), data(std::move(d)) {}
    SensorPayload(const SensorPayload&) = delete;
    SensorPayload& operator=(const SensorPayload&) = delete;
    SensorPayload(SensorPayload&&) noexcept = default;
    SensorPayload& operator=(SensorPayload&&) noexcept = default;
    ~SensorPayload() = default;
};

void run_basic_lifecycle_tests() {
    std::cout << "[ТЕСТ 1] Перевірка життєвого циклу цілочисельного буфера...\n";
    BoundedRingBuffer<int, 3> q;

    assert(q.empty());
    assert(q.size() == 0);
    assert(q.capacity() == 3);

    q.push(10);
    q.push(20);
    assert(q.size() == 2);
    assert(q.front() == 10);
    assert(q.back() == 20);

    q.push(30);
    assert(q.full());
    assert(q.size() == 3);

    q.pop(); // Видаляємо 10
    assert(!q.full());
    assert(q.size() == 2);
    assert(q.front() == 20);

    q.push(40); // Циклічний перехід хвоста через нульовий індекс
    assert(q.full());
    assert(q.back() == 40);

    q.clear();
    assert(q.empty());
    assert(q.size() == 0);
    std::cout << "  -> Життєвий цикл перевірено успішно.\n";
}

void run_move_semantics_tests() {
    std::cout << "[ТЕСТ 2] Перевірка роботи з move-only об'єктами...\n";
    BoundedRingBuffer<SensorPayload, 2> sensor_queue;

    sensor_queue.push(SensorPayload(101, "Telemetry_GPS_OK"));
    sensor_queue.push(SensorPayload(102, "Telemetry_IMU_OK"));

    assert(sensor_queue.full());
    assert(sensor_queue.front().sensor_id == 101);

    SensorPayload payload = std::move(sensor_queue.front());
    sensor_queue.pop();

    assert(payload.sensor_id == 101);
    assert(payload.data == "Telemetry_GPS_OK");
    assert(sensor_queue.size() == 1);
    std::cout << "  -> Семантику переміщення перевірено успішно.\n";
}

void run_simulated_contract_check() {
    std::cout << "[ТЕСТ 3] Симуляція контрактного контролю на межі місткості...\n";
    BoundedRingBuffer<int, 2> test_q;
    test_q.push(1);
    test_q.push(2);

    // У режимі збирання observe наступна операція викличе handle_contract_violation,
    // зафіксує запис у g_crash_log і дозволить програмі продовжити роботу.
    // У режимі збирання enforce виклик призведе до std::terminate().
    std::cout << "  Буфер заповнено. Спроба push(3) перевіряє pre [buffer_not_full].\n";
    // test_q.push(3); // Розкоментувати для активації збою
}

int main() {
    std::cout << "=====================================================\n";
    std::cout << "  Тестування BoundedRingBuffer з контрактами C++26   \n";
    std::cout << "=====================================================\n";

    run_basic_lifecycle_tests();
    run_move_semantics_tests();
    run_simulated_contract_check();

    std::cout << "Усі тести завершено успішно.\n";
    return 0;
}
