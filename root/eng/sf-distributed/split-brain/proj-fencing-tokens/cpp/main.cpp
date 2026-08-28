#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <cstdint>
#include <expected>
#include <memory>
#include <format>

// Коди помилок операцій зі сховищем
enum class StorageError {
    StaleEpoch,
    NotFound,
    InvalidToken
};

// Структура інформації про збережений запис
struct StorageEntry {
    std::string value;
    uint64_t last_modified_epoch;
};

// Запит на модифікацію даних із фенсинговим токеном
struct WriteRequest {
    uint64_t epoch;
    std::string_view key;
    std::string_view value;
};

// Сервер сховища ключ-значення з перевіркою епохи
class StorageServer {
public:
    StorageServer() : max_accepted_epoch_(0) {}

    // Атомарна обробка запиту на запис
    [[nodiscard]] std::expected<uint64_t, StorageError> write(const WriteRequest& req) {
        // Інваріант фенсингу: відхиляємо будь-яку епоху, меншу за max_accepted_epoch_
        if (req.epoch < max_accepted_epoch_) {
            return std::unexpected(StorageError::StaleEpoch);
        }

        // Оновлюємо найвищу зафіксовану епоху сховища
        max_accepted_epoch_ = req.epoch;

        // Зберігаємо або оновлюємо значення
        data_[std::string(req.key)] = StorageEntry{
            .value = std::string(req.value),
            .last_modified_epoch = req.epoch
        };

        return max_accepted_epoch_;
    }

    // Читання поточного значення
    [[nodiscard]] std::expected<std::string, StorageError> read(std::string_view key) const {
        auto it = data_.find(std::string(key));
        if (it == data_.end()) {
            return std::unexpected(StorageError::NotFound);
        }
        return it->second.value;
    }

    [[nodiscard]] uint64_t current_epoch() const noexcept {
        return max_accepted_epoch_;
    }

private:
    uint64_t max_accepted_epoch_;
    std::unordered_map<std::string, StorageEntry> data_;
};

// Координатор кластера, що генерує монотонні токени терму
class ClusterCoordinator {
public:
    ClusterCoordinator() : current_epoch_(0), active_leader_("None") {}

    // Вибори нового лідера з монотонним збільшенням токена
    uint64_t elect_leader(std::string_view new_leader_name) {
        ++current_epoch_;
        active_leader_ = new_leader_name;
        std::cout << std::format("[COORDINATOR] Elected new leader '{}' with Fencing Token (Epoch) = {}\n",
                                 active_leader_, current_epoch_);
        return current_epoch_;
    }

    [[nodiscard]] uint64_t current_epoch() const noexcept {
        return current_epoch_;
    }

    [[nodiscard]] std::string_view active_leader() const noexcept {
        return active_leader_;
    }

private:
    uint64_t current_epoch_;
    std::string active_leader_;
};

int main() {
    std::cout << "=== СИМУЛЯЦІЯ ЗАХИСТУ ВІД SPLIT-BRAIN ЧЕРЕЗ FENCING TOKENS (C++23) ===\n\n";

    StorageServer storage;
    ClusterCoordinator coordinator;

    // 1. Початкові вибори лідера
    const uint64_t leader1_token = coordinator.elect_leader("Node-1");

    // 2. Вузол 1 успішно записує дані на рахунок
    WriteRequest req1{
        .epoch = leader1_token,
        .key = "account:UA8842",
        .value = "balance:1000_UAH"
    };

    std::cout << std::format("[LEADER 1] Sending write: key='{}', val='{}', epoch={}\n",
                             req1.key, req1.value, req1.epoch);

    auto res1 = storage.write(req1);
    if (res1.has_value()) {
        std::cout << std::format("[STORAGE] SUCCESS: Write accepted, Current Server Epoch = {}\n\n", *res1);
    }

    // 3. Симуляція раптового зависання Вузла 1 (GC Pause)
    std::cout << ">>> [ALARM] Node-1 frozen on GC pause (Stop-The-World)! Heartbeat lost.\n";

    // 4. Координатор обирає Вузол 2 новим лідером
    const uint64_t leader2_token = coordinator.elect_leader("Node-2");

    // 5. Вузол 2 записує дані з токеном e=2
    WriteRequest req2{
        .epoch = leader2_token,
        .key = "account:UA8842",
        .value = "balance:750_UAH"
    };

    std::cout << std::format("[LEADER 2] Sending write: key='{}', val='{}', epoch={}\n",
                             req2.key, req2.value, req2.epoch);

    auto res2 = storage.write(req2);
    if (res2.has_value()) {
        std::cout << std::format("[STORAGE] SUCCESS: Write accepted, Current Server Epoch = {}\n\n", *res2);
    }

    // 6. Вузол 1 прокидається і надсилає запізнілий запис зі старим токеном e=1
    std::cout << ">>> [RESUME] Node-1 wakes up from GC! It still believes it is the leader.\n";
    WriteRequest stale_req{
        .epoch = leader1_token, // Старий токен = 1
        .key = "account:UA8842",
        .value = "balance:500_UAH" // Застаріле перезаписування
    };

    std::cout << std::format("[LEADER 1 (STALE)] Trying to write: key='{}', val='{}', epoch={}\n",
                             stale_req.key, stale_req.value, stale_req.epoch);

    auto stale_res = storage.write(stale_req);
    if (!stale_res.has_value()) {
        if (stale_res.error() == StorageError::StaleEpoch) {
            std::cout << std::format("[STORAGE] REJECTED: Stale fencing token! (ReqEpoch {} < ServerEpoch {})\n\n",
                                     stale_req.epoch, storage.current_epoch());
        }
    }

    // 7. Фінальна верифікація цілісності сховища
    auto final_value = storage.read("account:UA8842");
    if (final_value.has_value()) {
        std::cout << std::format("=== ПІДСУМОК: Фінальний стан у сховищі: '{}' ===\n", *final_value);
    }
    std::cout << "Цілісність збережено: запізнілий запис відхилено завдяки фенсингу.\n";

    return 0;
}
