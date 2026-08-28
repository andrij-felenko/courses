#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <shared_mutex>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <thread>
#include <format>
#include <memory>

enum class CacheState {
    Valid,
    Stale,
    Evicted
};

struct CachePayload {
    std::string body;
    std::chrono::system_clock::time_point expires_at;
    CacheState state{CacheState::Valid};
    std::vector<std::string> tags;
};

class EdgeCacheEngine {
public:
    void put(std::string_view url, std::string body, std::chrono::seconds ttl, 
             std::vector<std::string> tags) {
        std::unique_lock lock(mutex_);
        auto now = std::chrono::system_clock::now();
        
        CachePayload payload{
            .body = std::move(body),
            .expires_at = now + ttl,
            .state = CacheState::Valid,
            .tags = tags
        };
        
        std::string url_str(url);
        for (const auto& tag : tags) {
            tag_index_[tag].insert(url_str);
        }
        store_[url_str] = std::move(payload);
    }

    size_t purge_tag(std::string_view tag, bool soft = true) {
        std::unique_lock lock(mutex_);
        auto it = tag_index_.find(std::string(tag));
        if (it == tag_index_.end()) {
            return 0;
        }

        size_t count = 0;
        for (const auto& url : it->second) {
            if (auto sit = store_.find(url); sit != store_.end()) {
                sit->second.state = soft ? CacheState::Stale : CacheState::Evicted;
                ++count;
            }
        }
        return count;
    }

    std::string get_or_fetch(std::string_view url) {
        std::string url_str(url);
        std::shared_ptr<FlightControl> flight;

        {
            std::unique_lock lock(mutex_);
            auto now = std::chrono::system_clock::now();
            auto it = store_.find(url_str);

            // 1. Хіт валідного запису
            if (it != store_.end() && it->second.state == CacheState::Valid && it->second.expires_at > now) {
                return it->second.body;
            }

            // 2. Stale-While-Revalidate: повертаємо застарілу версію та тригеримо фонове оновлення
            bool has_stale = (it != store_.end() && (it->second.state == CacheState::Stale || it->second.expires_at <= now));
            std::string stale_body = has_stale ? it->second.body : "";

            auto& f = in_flight_[url_str];
            if (f) {
                if (has_stale) return stale_body;
                flight = f; // Чекаємо на активний запит
            } else {
                f = std::make_shared<FlightControl>();
                flight = f;
                // Запускаємо вибірку
                lock.unlock();
                auto fresh_data = fetch_from_origin(url_str);
                
                put(url_str, fresh_data, std::chrono::seconds(300), {"products", "catalog"});
                
                lock.lock();
                flight->result = fresh_data;
                flight->done = true;
                flight->cv.notify_all();
                in_flight_.erase(url_str);
                return fresh_data;
            }
        }

        // Очікування завершення лідера Single-Flight
        std::unique_lock flight_lock(flight->m);
        flight->cv.wait(flight_lock, [&] { return flight->done; });
        return flight->result;
    }

private:
    struct FlightControl {
        std::mutex m;
        std::condition_variable cv;
        bool done{false};
        std::string result;
    };

    std::string fetch_from_origin(const std::string& url) {
        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Імітація RTT
        auto now_sec = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
        return std::format(R"({{"url":"{}","price":199,"gen_time":{}}})", url, now_sec);
    }

    std::shared_mutex mutex_;
    std::unordered_map<std::string, CachePayload> store_;
    std::unordered_map<std::string, std::unordered_set<std::string>> tag_index_;
    std::unordered_map<std::string, std::shared_ptr<FlightControl>> in_flight_;
};
