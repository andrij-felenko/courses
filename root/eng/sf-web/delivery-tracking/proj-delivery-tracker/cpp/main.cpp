// C++20: Production Delivery Tracker & Monotonic State Machine

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <chrono>
#include <optional>
#include <functional>

namespace delivery {

enum class Status : int8_t {
    Expired = -3,
    FailedPermanent = -2,
    FailedTransient = -1,
    Created = 0,
    Dispatched = 1,
    Sent = 2,
    Delivered = 3,
    Opened = 4
};

enum class Channel {
    Push,
    Sms,
    Email
};

[[nodiscard]] constexpr int status_rank(Status s) noexcept {
    return static_cast<int>(s);
}

[[nodiscard]] constexpr std::string_view to_string(Status s) noexcept {
    switch (s) {
        case Status::Created: return "CREATED";
        case Status::Dispatched: return "DISPATCHED";
        case Status::Sent: return "SENT";
        case Status::Delivered: return "DELIVERED";
        case Status::Opened: return "OPENED";
        case Status::FailedTransient: return "FAILED_TRANSIENT";
        case Status::FailedPermanent: return "FAILED_PERMANENT";
        case Status::Expired: return "EXPIRED";
    }
    return "UNKNOWN";
}

struct Attempt {
    std::string attempt_id;
    Channel channel;
    std::string provider;
    std::string provider_msg_id;
    Status status{Status::Created};
    std::string error_code;
    std::chrono::system_clock::time_point dispatched_at;
    std::chrono::system_clock::time_point updated_at;
};

struct NotificationEnvelope {
    std::string id;
    std::string user_id;
    std::string title;
    std::string body;
    Status current_status{Status::Created};
    size_t current_channel_index{0};
    std::vector<Channel> cascade{Channel::Push, Channel::Sms, Channel::Email};
    std::vector<std::chrono::seconds> timeouts{
        std::chrono::seconds(45),
        std::chrono::seconds(60),
        std::chrono::seconds(120)
    };
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point expires_at;
    std::vector<Attempt> attempts;
    bool timer_active{false};
};

struct GatewayResult {
    bool success{false};
    std::string provider_msg_id;
    std::string error_code;
    bool is_permanent{false};
};

class IDeliveryGateway {
public:
    virtual ~IDeliveryGateway() = default;
    virtual GatewayResult send(
        std::string_view notification_id,
        Channel channel,
        std::string_view title,
        std::string_view body
    ) = 0;
};

class DeliveryTracker {
public:
    explicit DeliveryTracker(std::shared_ptr<IDeliveryGateway> gateway)
        : gateway_(std::move(gateway)) {}

    NotificationEnvelope& submit_notification(
        std::string id,
        std::string user_id,
        std::string title,
        std::string body,
        std::chrono::seconds ttl = std::chrono::seconds(300)
    ) {
        auto now = std::chrono::system_clock::now();
        NotificationEnvelope env{
            .id = std::move(id),
            .user_id = std::move(user_id),
            .title = std::move(title),
            .body = std::move(body),
            .current_status = Status::Created,
            .current_channel_index = 0,
            .cascade = {Channel::Push, Channel::Sms, Channel::Email},
            .timeouts = {std::chrono::seconds(45), std::chrono::seconds(60), std::chrono::seconds(120)},
            .created_at = now,
            .expires_at = now + ttl,
            .attempts = {},
            .timer_active = false
        };

        auto [it, _] = notifications_.insert_or_assign(env.id, std::move(env));
        execute_cascade_step(it->second);
        return it->second;
    }

    bool handle_dsn_webhook(
        std::string_view event_id,
        std::string_view notification_id,
        std::string_view provider_msg_id,
        Status status,
        std::string_view error_code = {}
    ) {
        if (processed_events_.contains(std::string(event_id))) {
            return true;
        }
        processed_events_.insert(std::string(event_id));

        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) {
            return false;
        }

        auto& env = it->second;

        for (auto& att : env.attempts) {
            if (att.provider_msg_id == provider_msg_id) {
                att.status = status;
                att.error_code = error_code;
                att.updated_at = std::chrono::system_clock::now();
                break;
            }
        }

        update_state_monotonic(env, status);

        if (status == Status::Delivered || status == Status::Opened) {
            env.timer_active = false;
        }

        return true;
    }

    bool record_user_open(std::string_view notification_id) {
        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) return false;

        it->second.timer_active = false;
        return update_state_monotonic(it->second, Status::Opened);
    }

    void check_and_trigger_fallback(std::string_view notification_id) {
        auto it = notifications_.find(std::string(notification_id));
        if (it == notifications_.end()) return;

        auto& env = it->second;
        if (!env.timer_active) return;

        if (status_rank(env.current_status) >= status_rank(Status::Delivered) ||
            env.current_status == Status::Expired) {
            env.timer_active = false;
            return;
        }

        env.current_channel_index++;
        execute_cascade_step(env);
    }

    [[nodiscard]] const NotificationEnvelope* get(std::string_view id) const {
        auto it = notifications_.find(std::string(id));
        return it != notifications_.end() ? &it->second : nullptr;
    }

private:
    void execute_cascade_step(NotificationEnvelope& env) {
        auto now = std::chrono::system_clock::now();

        if (now >= env.expires_at) {
            update_state_monotonic(env, Status::Expired);
            env.timer_active = false;
            return;
        }

        if (env.current_channel_index >= env.cascade.size()) {
            update_state_monotonic(env, Status::FailedPermanent);
            env.timer_active = false;
            return;
        }

        auto channel = env.cascade[env.current_channel_index];
        Attempt att{
            .attempt_id = env.id + "_att_" + std::to_string(env.current_channel_index + 1),
            .channel = channel,
            .provider = channel == Channel::Push ? "APNS_FCM" : channel == Channel::Sms ? "TWILIO" : "AWS_SES",
            .provider_msg_id = "",
            .status = Status::Dispatched,
            .error_code = "",
            .dispatched_at = now,
            .updated_at = now
        };
        env.attempts.push_back(att);
        update_state_monotonic(env, Status::Dispatched);
        env.timer_active = true;

        auto res = gateway_->send(env.id, channel, env.title, env.body);
        auto& current_att = env.attempts.back();
        current_att.updated_at = std::chrono::system_clock::now();

        if (res.success) {
            current_att.provider_msg_id = res.provider_msg_id;
            current_att.status = Status::Sent;
            update_state_monotonic(env, Status::Sent);
        } else {
            current_att.error_code = res.error_code;
            if (res.is_permanent) {
                current_att.status = Status::FailedPermanent;
                env.timer_active = false;
                env.current_channel_index++;
                execute_cascade_step(env);
            } else {
                current_att.status = Status::FailedTransient;
            }
        }
    }

    bool update_state_monotonic(NotificationEnvelope& env, Status new_status) noexcept {
        int current_r = status_rank(env.current_status);
        int new_r = status_rank(new_status);

        if (new_r < 0) {
            if (current_r < status_rank(Status::Delivered)) {
                env.current_status = new_status;
                return true;
            }
            return false;
        }

        if (new_r > current_r) {
            env.current_status = new_status;
            return true;
        }
        return false;
    }

    std::shared_ptr<IDeliveryGateway> gateway_;
    std::unordered_map<std::string, NotificationEnvelope> notifications_;
    std::unordered_set<std::string> processed_events_;
};

} // namespace delivery
