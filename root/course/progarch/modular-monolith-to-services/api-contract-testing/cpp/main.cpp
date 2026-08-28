// C++17: Обробник станів Провайдера (Provider States) з використанням std::unordered_map та std::function
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <functional>

class ProviderStateRegistry {
public:
    using StateSetupHandler = std::function<bool(std::string_view params_json)>;

    void register_state(std::string state_name, StateSetupHandler handler) {
        handlers_[std::move(state_name)] = std::move(handler);
    }

    bool handle_state_setup(std::string_view requested_state, std::string_view params_json) const {
        auto it = handlers_.find(std::string(requested_state));
        if (it != handlers_.end()) {
            return it->second(params_json);
        }
        std::cerr << "[PACT STATE ERROR] Unknown provider state requested: " << requested_state << "\n";
        return false;
    }

private:
    std::unordered_map<std::string, StateSetupHandler> handlers_;
};

// Приклад підключення станів у контролері Провайдера
inline void register_telemetry_provider_states(ProviderStateRegistry& registry) {
    registry.register_state("device with ID 105 has historical telemetry readings", [](std::string_view params) {
        std::cout << "[PACT STATE SETUP] Seeding DB: INSERT INTO telemetry (device_id, temp) VALUES (105, 22.5);\n";
        return true;
    });

    registry.register_state("device with ID 99999 does not exist", [](std::string_view params) {
        std::cout << "[PACT STATE SETUP] Seeding DB: DELETE FROM telemetry WHERE device_id = 99999;\n";
        return true;
    });
}
