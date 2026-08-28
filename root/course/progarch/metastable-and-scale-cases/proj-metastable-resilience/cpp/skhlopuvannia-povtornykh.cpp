// C++ Implementation: Singleflight Request Coalescer (unordered_map, condition_variable, shared_ptr)
#include <iostream>
#include <string>
#include <unordered_map>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <memory>

template <typename T>
class SingleflightGroup {
public:
    SingleflightGroup() = default;

    T execute(const std::string& key, std::function<T(const std::string&)> fetch_fn) {
        std::shared_ptr<Call> call;

        {
            std::unique_lock<std::mutex> lock(mutex_);
            auto it = calls_.find(key);
            if (it != calls_.end()) {
                call = it->second; // Joined active call
                lock.unlock();

                std::unique_lock<std::mutex> call_lock(call->call_mutex);
                call->cond.wait(call_lock, [&call]() { return call->done; });
                return call->result;
            }

            call = std::make_shared<Call>();
            calls_[key] = call;
        }

        // Execute origin fetch outside table lock
        call->result = fetch_fn(key);

        {
            std::lock_guard<std::mutex> call_lock(call->call_mutex);
            call->done = true;
        }
        call->cond.notify_all();

        {
            std::lock_guard<std::mutex> lock(mutex_);
            calls_.erase(key);
        }

        return call->result;
    }

private:
    struct Call {
        T result;
        bool done{false};
        std::mutex call_mutex;
        std::condition_variable cond;
    };

    std::mutex mutex_;
    std::unordered_map<std::string, std::shared_ptr<Call>> calls_;
};
