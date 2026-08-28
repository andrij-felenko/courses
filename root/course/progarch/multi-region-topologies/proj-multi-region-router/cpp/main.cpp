#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <cstdint>

// Послідовна позначка журналу транзакцій (LSN)
using Lsn = uint64_t;

// Перелік доступних глобальних регіонів
enum class Region {
    Frankfurt_Primary,
    Virginia_Replica,
    Tokyo_Replica
};

// Перетворення регіону у рядок для логування
constexpr std::string_view region_to_string(Region r) noexcept {
    switch (r) {
        case Region::Frankfurt_Primary: return "eu-central-1 (Primary)";
        case Region::Virginia_Replica:  return "us-east-1 (Replica)";
        case Region::Tokyo_Replica:     return "ap-northeast-1 (Replica)";
    }
    return "unknown";
}

// Конверт запиту з гео-метаданими
struct HttpRequest {
    std::string path;
    bool is_write_method{false};
    Region client_region{Region::Tokyo_Replica};
    std::optional<Lsn> required_lsn; // Токен Read-After-Write (X-LSN Header)
};

// Структура відповіді сервера
struct HttpResponse {
    int status_code{200};
    std::string body;
    Region served_by_region{Region::Frankfurt_Primary};
    std::optional<Lsn> new_lsn; // Повертається при записі
};

// Інтерфейс вузла бази даних
class IDatabaseNode {
public:
    virtual ~IDatabaseNode() = default;
    [[nodiscard]] virtual Region get_region() const noexcept = 0;
    [[nodiscard]] virtual Lsn get_current_lsn() const noexcept = 0;
    [[nodiscard]] virtual HttpResponse execute_read(const HttpRequest& req) = 0;
    [[nodiscard]] virtual HttpResponse execute_write(const HttpRequest& req) = 0;
};

// Реалізація Primary-вузла бази даних у Франкфурті
class PrimaryDatabase final : public IDatabaseNode {
private:
    Lsn current_lsn_{4000};

public:
    Region get_region() const noexcept override {
        return Region::Frankfurt_Primary;
    }

    Lsn get_current_lsn() const noexcept override {
        return current_lsn_;
    }

    HttpResponse execute_read(const HttpRequest& req) override {
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"ok\", \"data\": \"fresh_primary_state\"}",
            .served_by_region = Region::Frankfurt_Primary,
            .new_lsn = current_lsn_
        };
    }

    HttpResponse execute_write(const HttpRequest& req) override {
        ++current_lsn_; // Монотонний приріст LSN при кожному записі
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"written\", \"lsn\": " + std::to_string(current_lsn_) + "}",
            .served_by_region = Region::Frankfurt_Primary,
            .new_lsn = current_lsn_
        };
    }
};

// Реалізація Read-репліки у віддаленому регіоні
class ReadReplica final : public IDatabaseNode {
private:
    Region region_;
    Lsn replicated_lsn_{3950}; // Репліка відстає від Primary

public:
    explicit ReadReplica(Region region, Lsn initial_lsn)
        : region_(region), replicated_lsn_(initial_lsn) {}

    Region get_region() const noexcept override {
        return region_;
    }

    Lsn get_current_lsn() const noexcept override {
        return replicated_lsn_;
    }

    void update_replication_lsn(Lsn new_lsn) noexcept {
        replicated_lsn_ = new_lsn;
    }

    HttpResponse execute_read(const HttpRequest& req) override {
        return HttpResponse{
            .status_code = 200,
            .body = "{\"status\": \"ok\", \"data\": \"local_replica_state\"}",
            .served_by_region = region_,
            .new_lsn = replicated_lsn_
        };
    }

    HttpResponse execute_write(const HttpRequest& req) override {
        // Read Replica не приймає записи
        return HttpResponse{
            .status_code = 405,
            .body = "{\"error\": \"Method Not Allowed on Replica\"}",
            .served_by_region = region_,
            .new_lsn = std::nullopt
        };
    }
};

// Розумний міжрегіональний маршрутизатор
class GeoAwareRouter {
private:
    std::shared_ptr<PrimaryDatabase> primary_db_;
    std::unordered_map<Region, std::shared_ptr<ReadReplica>> replicas_;

public:
    explicit GeoAwareRouter(std::shared_ptr<PrimaryDatabase> primary)
        : primary_db_(std::move(primary)) {}

    void register_replica(Region region, std::shared_ptr<ReadReplica> replica) {
        replicas_[region] = std::move(replica);
    }

    // Головний метод маршрутизації запиту
    [[nodiscard]] HttpResponse route_request(const HttpRequest& req) {
        // 1. Усі записи безвинятково йдуть на Primary у Франкфурт
        if (req.is_write_method) {
            std::cout << "[Router] Write request -> Routing to Primary in "
                      << region_to_string(primary_db_->get_region()) << "\n";
            return primary_db_->execute_write(req);
        }

        // 2. Якщо це читання, шукаємо найближчу локальну репліку
        auto it = replicas_.find(req.client_region);
        if (it == replicas_.end()) {
            // Немає репліки у регіоні -> йдемо на Primary
            std::cout << "[Router] No local replica -> Fallback to Primary\n";
            return primary_db_->execute_read(req);
        }

        const auto& local_replica = it->second;

        // 3. Перевірка Read-After-Write узгодженості (LSN Token Check)
        if (req.required_lsn.has_value()) {
            Lsn target_lsn = req.required_lsn.value();
            Lsn replica_lsn = local_replica->get_current_lsn();

            if (replica_lsn < target_lsn) {
                // Виявлено лаг реплікації! Локальні дані застаріли.
                std::cout << "[Router] RAW Check Failed! Client LSN: " << target_lsn
                          << ", Replica LSN: " << replica_lsn
                          << " (Lag: " << (target_lsn - replica_lsn) << " ops)"
                          << " -> Fallback to Primary in Frankfurt!\n";
                return primary_db_->execute_read(req);
            }
        }

        // 4. Локальна репліка свіжа -> віддаємо локальне швидке читання
        std::cout << "[Router] Local Replica LSN is fresh -> Serving locally in "
                  << region_to_string(local_replica->get_region()) << "\n";
        return local_replica->execute_read(req);
    }
};

int main() {
    // Ініціалізація кластера
    auto primary = std::make_shared<PrimaryDatabase>();
    auto tokyo_replica = std::make_shared<ReadReplica>(Region::Tokyo_Replica, 4000);

    GeoAwareRouter router(primary);
    router.register_replica(Region::Tokyo_Replica, tokyo_replica);

    std::cout << "=== Крок 1: Користувач у Токіо робить запис (PUT) ===\n";
    HttpRequest write_req{
        .path = "/api/v1/homes/h-101/devices/lamp",
        .is_write_method = true,
        .client_region = Region::Tokyo_Replica,
        .required_lsn = std::nullopt
    };

    HttpResponse write_resp = router.route_request(write_req);
    Lsn issued_token = write_resp.new_lsn.value_or(0);
    std::cout << "Відповідь запису: " << write_resp.body
              << " | Отримано токен X-LSN=" << issued_token << "\n\n";

    std::cout << "=== Крок 2: Негайне читання (GET) з токеном LSN=" << issued_token << " ===\n";
    HttpRequest read_req1{
        .path = "/api/v1/homes/h-101/devices",
        .is_write_method = false,
        .client_region = Region::Tokyo_Replica,
        .required_lsn = issued_token
    };

    // Оскільки tokyo_replica ще має LSN=4000, а токен=401, буде виконано фолбек на Primary
    HttpResponse read_resp1 = router.route_request(read_req1);
    std::cout << "Результат читання 1: " << read_resp1.body
              << " | Оброблено регіоном: " << region_to_string(read_resp1.served_by_region) << "\n\n";

    std::cout << "=== Крок 3: Синхронізація репліки Токіо до LSN=" << issued_token << " ===\n";
    tokyo_replica->update_replication_lsn(issued_token);

    std::cout << "=== Крок 4: Повторне читання (GET) з тим самим токеном ===\n";
    HttpResponse read_resp2 = router.route_request(read_req1);
    std::cout << "Результат читання 2: " << read_resp2.body
              << " | Оброблено регіоном: " << region_to_string(read_resp2.served_by_region) << "\n";

    return 0;
}
