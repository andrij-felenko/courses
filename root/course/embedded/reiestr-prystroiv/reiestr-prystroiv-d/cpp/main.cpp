#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <optional>
#include <chrono>
#include <algorithm>
#include <functional>

// 1. Модель сутності пристрою
struct HardwareIdentity {
    std::string silicon_uid;
    std::string hw_revision;
    std::string mac_address;
    std::string cert_fingerprint;
};

struct SystemState {
    std::string firmware_version;
    bool is_online{false};
    int rssi_dbm{-100};
    double battery_soc{1.0}; // 0.0 .. 1.0 (100%)
    std::chrono::system_clock::time_point last_seen;
};

struct DeviceEntity {
    std::string device_uuid;
    HardwareIdentity hardware;
    SystemState system;
    std::unordered_map<std::string, std::string> tags;

    std::optional<std::string> get_attribute(const std::string& path) const {
        if (path == "sys.firmware_version") return system.firmware_version;
        if (path == "sys.is_online") return system.is_online ? "true" : "false";
        if (path == "hw.revision") return hardware.hw_revision;
        if (path.rfind("tags.", 0) == 0) {
            std::string tag_key = path.substr(5);
            auto it = tags.find(tag_key);
            if (it != tags.end()) return it->second;
        }
        return std::nullopt;
    }
};

// 2. Декларативний рушій вибірок (AST Query Engine)
class Expression {
public:
    virtual ~Expression() = default;
    virtual bool evaluate(const DeviceEntity& device) const = 0;
};

// Порівняння атрибута зі значенням
class ComparisonExpr : public Expression {
public:
    enum class Op { Equal, NotEqual, LessThan, GreaterThan };

    ComparisonExpr(std::string attr_path, Op op, std::string target_val)
        : attr_path_(std::move(attr_path)), op_(op), target_val_(std::move(target_val)) {}

    bool evaluate(const DeviceEntity& device) const override {
        auto val = device.get_attribute(attr_path_);
        if (!val.has_value()) return false;

        switch (op_) {
            case Op::Equal: return *val == target_val_;
            case Op::NotEqual: return *val != target_val_;
            case Op::LessThan: return *val < target_val_;
            case Op::GreaterThan: return *val > target_val_;
        }
        return false;
    }

private:
    std::string attr_path_;
    Op op_;
    std::string target_val_;
};

// Логічне AND
class AndExpr : public Expression {
public:
    AndExpr(std::unique_ptr<Expression> left, std::unique_ptr<Expression> right)
        : left_(std::move(left)), right_(std::move(right)) {}

    bool evaluate(const DeviceEntity& device) const override {
        return left_->evaluate(device) && right_->evaluate(device);
    }

private:
    std::unique_ptr<Expression> left_;
    std::unique_ptr<Expression> right_;
};

// 3. Серверний реєстр пристроїв із інвертованим індексом
class DeviceRegistry {
public:
    void register_device(DeviceEntity device) {
        std::string id = device.device_uuid;
        // Оновлюємо інвертований індекс за тегами
        for (const auto& [k, v] : device.tags) {
            tag_index_[k + "=" + v].push_back(id);
        }
        devices_[id] = std::move(device);
    }

    void update_firmware(const std::string& device_uuid, const std::string& new_version) {
        auto it = devices_.find(device_uuid);
        if (it != devices_.end()) {
            it->second.system.firmware_version = new_version;
            it->second.system.last_seen = std::chrono::system_clock::now();
        }
    }

    void set_connection_status(const std::string& device_uuid, bool online) {
        auto it = devices_.find(device_uuid);
        if (it != devices_.end()) {
            it->second.system.is_online = online;
            it->second.system.last_seen = std::chrono::system_clock::now();
        }
    }

    // Виконання динамічної вибірки над парком
    std::vector<std::string> query_devices(const Expression& query) const {
        std::vector<std::string> matched_ids;
        for (const auto& [id, dev] : devices_) {
            if (query.evaluate(dev)) {
                matched_ids.push_back(id);
            }
        }
        return matched_ids;
    }

    const DeviceEntity* get_device(const std::string& id) const {
        auto it = devices_.find(id);
        return it != devices_.end() ? &it->second : nullptr;
    }

private:
    std::unordered_map<std::string, DeviceEntity> devices_;
    std::unordered_map<std::string, std::vector<std::string>> tag_index_;
};

int main() {
    DeviceRegistry registry;

    // Реєстрація тестового парку вузлів
    registry.register_device({
        .device_uuid = "dev-uuid-001",
        .hardware = {"CHIP-96-01", "revB", "00:1A:2B:3C:4D:5E", "sha256:abc1"},
        .system = {.firmware_version = "v2.1.3", .is_online = true, .battery_soc = 0.88},
        .tags = {{"env", "prod"}, {"site", "dnipro-14"}, {"role", "meter"}}
    });

    registry.register_device({
        .device_uuid = "dev-uuid-002",
        .hardware = {"CHIP-96-02", "revA", "00:1A:2B:3C:4D:5F", "sha256:abc2"},
        .system = {.firmware_version = "v2.1.3", .is_online = true, .battery_soc = 0.95},
        .tags = {{"env", "prod"}, {"site", "kyiv-02"}, {"role", "meter"}}
    });

    registry.register_device({
        .device_uuid = "dev-uuid-003",
        .hardware = {"CHIP-96-03", "revB", "00:1A:2B:3C:4D:60", "sha256:abc3"},
        .system = {.firmware_version = "v2.2.0", .is_online = true, .battery_soc = 0.75},
        .tags = {{"env", "prod"}, {"site", "dnipro-14"}, {"role", "meter"}}
    });

    // Формування динамічної вибірки для цільового OTA-оновлення:
    // "tags.env == 'prod' AND hw.revision == 'revB' AND sys.firmware_version < 'v2.2.0'"
    auto query_env = std::make_unique<ComparisonExpr>("tags.env", ComparisonExpr::Op::Equal, "prod");
    auto query_hw = std::make_unique<ComparisonExpr>("hw.revision", ComparisonExpr::Op::Equal, "revB");
    auto query_fw = std::make_unique<ComparisonExpr>("sys.firmware_version", ComparisonExpr::Op::LessThan, "v2.2.0");

    auto target_query = std::make_unique<AndExpr>(
        std::move(query_env),
        std::make_unique<AndExpr>(std::move(query_hw), std::move(query_fw))
    );

    std::cout << "=== Цільова динамічна вибірка для OTA ===" << std::endl;
    auto targets = registry.query_devices(*target_query);
    for (const auto& id : targets) {
        std::cout << "Цільовий пристрій для оновлення: " << id << std::endl;
    }

    // Симуляція успішного оновлення прошивки на вузлі dev-uuid-001
    std::cout << "\n[OTA] Оновлення вузла dev-uuid-001 до v2.2.0..." << std::endl;
    registry.update_firmware("dev-uuid-001", "v2.2.0");

    // Повторне обчислення вибірки — вузол має автоматично вибути
    auto post_targets = registry.query_devices(*target_query);
    std::cout << "Пристроїв у черзі після оновлення: " << post_targets.size() << std::endl;

    return 0;
}
