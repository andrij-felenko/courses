#include <variant>
#include <mutex>
#include <shared_mutex>
#include <string>

class ThreadSafeState {
    using State = std::variant<int, std::string>;
    State state_;
    mutable std::shared_mutex rw_mutex_;

public:
    State get_state() const {
        std::shared_lock lock(rw_mutex_);
        return state_;
    }

    void set_state(State new_state) {
        std::unique_lock lock(rw_mutex_);
        state_ = std::move(new_state);
    }
};
