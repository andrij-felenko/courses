// C++20 implementation
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <typeindex>
#include <optional>
#include <chrono>
#include <iostream>

// ── 1. Публічна доменна подія ──
struct DeviceStateChangedEvent {
    std::string event_id;
    std::string device_id;
    std::string home_id;
    std::string property_name;
    std::string old_value;
    std::string new_value;
    std::chrono::system_clock::time_point timestamp;
};

// ── 2. Публічний DTO та Інтерфейс (Pure Abstract Class) ──
struct DeviceDTO {
    std::string id;
    std::string home_id;
    std::string model;
    bool is_online;
};

class IDeviceRegistryModule {
public:
    virtual ~IDeviceRegistryModule() = default;
    virtual std::optional<DeviceDTO> get_device(const std::string& device_id) = 0;
    virtual std::vector<DeviceDTO> list_home_devices(const std::string& home_id) = 0;
};

// ── 3. Внутрішньопроцесна шина подій (InMemoryEventBus) ──
class InMemoryEventBus {
private:
    using HandlerList = std::vector<std::function<void(const void*)>>;
    std::unordered_map<std::type_index, HandlerList> handlers_;

public:
    template<typename EventType>
    void subscribe(std::function<void(const EventType&)> handler) {
        handlers_[typeid(EventType)].push_back([handler](const void* evt_ptr) {
            handler(*static_cast<const EventType*>(evt_ptr));
        });
    }

    template<typename EventType>
    void publish(const EventType& event) {
        auto it = handlers_.find(typeid(EventType));
        if (it != handlers_.end()) {
            for (const auto& handler : it->second) {
                try {
                    handler(&event);
                } catch (const std::exception& ex) {
                    std::cerr << "[EventBus Error] Exception in handler: " << ex.what() << '\n';
                }
            }
        }
    }
};
