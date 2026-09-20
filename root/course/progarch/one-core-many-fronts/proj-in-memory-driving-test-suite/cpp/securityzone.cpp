#pragma once

#include <string>
#include <unordered_map>
#include <vector>
#include <optional>

namespace dh::core {

struct SecurityZone {
    std::string id;
    std::string pin_code;
    bool has_open_sensors{false};
    bool is_armed{false};
};

class SecurityZoneRepository {
public:
    virtual ~SecurityZoneRepository() = default;
    virtual std::optional<SecurityZone> find_by_id(const std::string& id) = 0;
    virtual void save(const SecurityZone& zone) = 0;
};

class ActuatorEventBus {
public:
    virtual ~ActuatorEventBus() = default;
    virtual void publish_event(const std::string& event_type, const std::string& payload) = 0;
};

class InMemorySecurityZoneRepository : public SecurityZoneRepository {
public:
    std::optional<SecurityZone> find_by_id(const std::string& id) override {
        auto it = zones_.find(id);
        if (it == zones_.end()) return std::nullopt;
        return it->second;
    }

    void save(const SecurityZone& zone) override {
        zones_[zone.id] = zone;
    }

private:
    std::unordered_map<std::string, SecurityZone> zones_;
};

class ActuatorEventSpy : public ActuatorEventBus {
public:
    void publish_event(const std::string& event_type, const std::string& payload) override {
        emitted_events_.push_back(event_type + ":" + payload);
    }

    const std::vector<std::string>& emitted_events() const {
        return emitted_events_;
    }

private:
    std::vector<std::string> emitted_events_;
};

} // namespace dh::core
