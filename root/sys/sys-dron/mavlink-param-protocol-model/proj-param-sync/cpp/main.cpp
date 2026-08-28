#include <cstdint>
#include <cstring>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <variant>
#include <chrono>
#include <functional>
#include <bit>
#include <iostream>

class ParameterSyncEngine {
public:
    using ParamValue = std::variant<uint8_t, int8_t, uint16_t, int16_t, uint32_t, int32_t, float>;

    struct Parameter {
        std::string name;
        ParamValue  value;
        uint8_t     mav_type{0};
        uint16_t    index{0};
    };

    enum class State {
        Idle,
        RequestingList,
        ReceivingBurst,
        ResolvingHoles,
        Completed,
        Failed
    };

    using SendListCallback = std::function<void(uint8_t sys_id, uint8_t comp_id)>;
    using SendReadCallback = std::function<void(uint8_t sys_id, uint8_t comp_id, int16_t index)>;

    ParameterSyncEngine(uint8_t sys_id, uint8_t comp_id,
                        SendListCallback send_list,
                        SendReadCallback send_read)
        : target_system_(sys_id)
        , target_component_(comp_id)
        , send_list_fn_(std::move(send_list))
        , send_read_fn_(std::move(send_read)) {}

    void start(std::chrono::steady_clock::time_point now) {
        state_ = State::RequestingList;
        param_count_ = 0;
        received_count_ = 0;
        retry_count_ = 0;
        received_mask_.clear();
        params_by_index_.clear();
        params_by_name_.clear();
        last_activity_ = now;

        if (send_list_fn_) {
            send_list_fn_(target_system_, target_component_);
        }
    }

    void on_param_value(const char wire_id[16],
                        float raw_val,
                        uint8_t mav_type,
                        uint16_t total_count,
                        uint16_t index,
                        std::chrono::steady_clock::time_point now) {
        last_activity_ = now;

        if (param_count_ == 0 && total_count > 0) {
            param_count_ = total_count;
            received_mask_.resize(param_count_, false);
            params_by_index_.resize(param_count_);
        }

        if (index >= param_count_) {
            return;
        }

        if (!received_mask_[index]) {
            received_mask_[index] = true;
            received_count_++;

            const size_t id_len = strnlen(wire_id, 16);
            std::string name(wire_id, id_len);

            Parameter param{
                .name = name,
                .value = unpack_wire_value(raw_val, mav_type),
                .mav_type = mav_type,
                .index = index
            };

            params_by_index_[index] = param;
            params_by_name_[name] = param;
        }

        if (state_ == State::RequestingList) {
            state_ = State::ReceivingBurst;
        } else if (state_ == State::ResolvingHoles && index == current_hole_index_) {
            retry_count_ = 0;
        }
    }

    void poll(std::chrono::steady_clock::time_point now) {
        using namespace std::chrono_literals;

        switch (state_) {
            case State::RequestingList:
                if (now - last_activity_ > 1000ms) {
                    if (retry_count_ < max_list_retries_) {
                        retry_count_++;
                        last_activity_ = now;
                        send_list_fn_(target_system_, target_component_);
                    } else {
                        state_ = State::Failed;
                    }
                }
                break;

            case State::ReceivingBurst:
                if (received_count_ >= param_count_ && param_count_ > 0) {
                    state_ = State::Completed;
                } else if (now - last_activity_ > 500ms) {
                    advance_to_next_hole(now, 0);
                }
                break;

            case State::ResolvingHoles:
                if (current_hole_index_ < received_mask_.size() && received_mask_[current_hole_index_]) {
                    advance_to_next_hole(now, current_hole_index_ + 1);
                } else if (now - last_activity_ > 800ms) {
                    if (retry_count_ < max_hole_retries_) {
                        retry_count_++;
                        last_activity_ = now;
                        send_read_fn_(target_system_, target_component_, static_cast<int16_t>(current_hole_index_));
                    } else {
                        state_ = State::Failed;
                    }
                }
                break;

            case State::Idle:
            case State::Completed:
            case State::Failed:
                break;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] double progress() const noexcept {
        return param_count_ > 0 ? (100.0 * received_count_ / param_count_) : 0.0;
    }

    [[nodiscard]] const Parameter* get_by_name(std::string_view name) const noexcept {
        auto it = params_by_name_.find(std::string(name));
        return (it != params_by_name_.end()) ? &it->second : nullptr;
    }

    [[nodiscard]] const Parameter* get_by_index(uint16_t index) const noexcept {
        if (index < params_by_index_.size() && received_mask_[index]) {
            return &params_by_index_[index];
        }
        return nullptr;
    }

private:
    void advance_to_next_hole(std::chrono::steady_clock::time_point now, size_t start_idx) {
        for (size_t i = start_idx; i < received_mask_.size(); ++i) {
            if (!received_mask_[i]) {
                state_ = State::ResolvingHoles;
                current_hole_index_ = static_cast<uint16_t>(i);
                retry_count_ = 0;
                last_activity_ = now;
                send_read_fn_(target_system_, target_component_, static_cast<int16_t>(i));
                return;
            }
        }
        state_ = (received_count_ >= param_count_) ? State::Completed : State::Failed;
    }

    static ParamValue unpack_wire_value(float wire_float, uint8_t type) noexcept {
        const auto raw_u32 = std::bit_cast<uint32_t>(wire_float);
        switch (type) {
            case 1: return static_cast<uint8_t>(raw_u32 & 0xFF);
            case 2: return static_cast<int8_t>(static_cast<int32_t>(raw_u32) & 0xFF);
            case 3: return static_cast<uint16_t>(raw_u32 & 0xFFFF);
            case 4: return static_cast<int16_t>(static_cast<int32_t>(raw_u32) & 0xFFFF);
            case 5: return raw_u32;
            case 6: return std::bit_cast<int32_t>(raw_u32);
            case 9: return wire_float;
            default: return raw_u32;
        }
    }

    uint8_t target_system_;
    uint8_t target_component_;
    SendListCallback send_list_fn_;
    SendReadCallback send_read_fn_;

    State state_{State::Idle};
    uint16_t param_count_{0};
    uint16_t received_count_{0};
    uint16_t current_hole_index_{0};
    uint8_t  retry_count_{0};

    const uint8_t max_list_retries_{3};
    const uint8_t max_hole_retries_{5};

    std::vector<bool> received_mask_;
    std::vector<Parameter> params_by_index_;
    std::unordered_map<std::string, Parameter> params_by_name_;
    std::chrono::steady_clock::time_point last_activity_{};
};
