/**
 * Високопродуктивний C++20 Edge Proxy Worker з безпечним пулом потоків,
 * LRU-кешем та асинхронним stale-while-revalidate конвеєром.
 */

#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <list>
#include <mutex>
#include <chrono>
#include <memory>
#include <vector>
#include <optional>
#include <future>
#include <algorithm>

namespace edge {

struct HttpResponse {
    int status_code{200};
    std::unordered_map<std::string, std::string> headers;
    std::vector<uint8_t> body;
};

struct CacheEntry {
    HttpResponse response;
    std::chrono::steady_clock::time_point cached_at;
    std::chrono::seconds max_age{60};
    std::chrono::seconds stale_window{300};
};

class ThreadSafeLruCache {
public:
    explicit ThreadSafeLruCache(size_t capacity) : capacity_(capacity) {}

    std::optional<CacheEntry> get(std::string_view key) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = index_.find(std::string(key));
        if (it == index_.end()) {
            return std::nullopt;
        }
        // Переміщення використаного елемента в початок LRU-списку
        lru_order_.splice(lru_order_.begin(), lru_order_, it->second);
        return it->second->second;
    }

    void put(std::string_view key, CacheEntry entry) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::string k(key);
        auto it = index_.find(k);
        if (it != index_.end()) {
            it->second->second = std::move(entry);
            lru_order_.splice(lru_order_.begin(), lru_order_, it->second);
            return;
        }

        if (index_.size() >= capacity_) {
            // Витіснення найменш використовуваного елемента з кінця
            auto oldest = lru_order_.back().first;
            index_.erase(oldest);
            lru_order_.pop_back();
        }

        lru_order_.emplace_front(k, std::move(entry));
        index_[k] = lru_order_.begin();
    }

private:
    size_t capacity_;
    std::mutex mutex_;
    std::list<std::pair<std::string, CacheEntry>> lru_order_;
    std::unordered_map<std::string, decltype(lru_order_.begin())> index_;
};

class EdgeProxyWorker {
public:
    explicit EdgeProxyWorker(size_t cache_capacity) 
        : cache_(std::make_unique<ThreadSafeLruCache>(cache_capacity)) {}

    /**
     * Нормалізація ключа кешування: видалення маркетингових міток
     */
    static std::string normalize_url(std::string_view url) {
        auto query_pos = url.find('?');
        if (query_pos == std::string_view::npos) {
            return std::string(url);
        }
        std::string base(url.substr(0, query_pos));
        std::string_view query = url.substr(query_pos + 1);
        
        // Фільтрація query-параметрів
        std::vector<std::string> clean_params;
        size_t start = 0;
        while (start < query.size()) {
            auto amp = query.find('&', start);
            auto param = query.substr(start, amp == std::string_view::npos ? amp : amp - start);
            if (!param.starts_with("utm_") && !param.starts_with("gclid=")) {
                clean_params.emplace_back(param);
            }
            if (amp == std::string_view::npos) break;
            start = amp + 1;
        }
        std::sort(clean_params.begin(), clean_params.end());
        
        if (clean_params.empty()) return base;
        std::string result = base + "?";
        for (size_t i = 0; i < clean_params.size(); ++i) {
            result += clean_params[i];
            if (i + 1 < clean_params.size()) result += "&";
        }
        return result;
    }

    /**
     * Головний конвеєр обробки вхідного HTTP-запиту
     */
    HttpResponse handle_request(std::string_view method, std::string_view raw_url, 
                               const std::unordered_map<std::string, std::string>& headers) {
        if (method != "GET" && method != "HEAD") {
            return fetch_from_origin(raw_url, headers);
        }

        std::string cache_key = normalize_url(raw_url);
        auto now = std::chrono::steady_clock::now();
        auto cached = cache_->get(cache_key);

        if (cached.has_value()) {
            auto age = std::chrono::duration_cast<std::chrono::seconds>(now - cached->cached_at);
            
            // 1. Fresh Hit: миттєва віддача з пам'яті
            if (age <= cached->max_age) {
                auto resp = cached->response;
                resp.headers["X-Cache-Status"] = "HIT";
                resp.headers["Age"] = std::to_string(age.count());
                return resp;
            }

            // 2. Stale-While-Revalidate Hit: повертаємо застарілу версію та оновлюємо у фоні
            if (age <= (cached->max_age + cached->stale_window)) {
                // Асинхронний запуск фонового оновлення
                std::string url_copy(raw_url);
                auto headers_copy = headers;
                std::thread([this, cache_key, url_copy, headers_copy]() {
                    auto fresh_resp = fetch_from_origin(url_copy, headers_copy);
                    if (fresh_resp.status_code == 200) {
                        CacheEntry new_entry{
                            .response = std::move(fresh_resp),
                            .cached_at = std::chrono::steady_clock::now(),
                            .max_age = std::chrono::seconds(60),
                            .stale_window = std::chrono::seconds(300)
                        };
                        cache_->put(cache_key, std::move(new_entry));
                    }
                }).detach();

                auto resp = cached->response;
                resp.headers["X-Cache-Status"] = "STALE";
                resp.headers["Age"] = std::to_string(age.count());
                return resp;
            }
        }

        // 3. Cache Miss: пряме синхронне звернення до центрального сервера
        auto origin_resp = fetch_from_origin(raw_url, headers);
        if (origin_resp.status_code == 200) {
            CacheEntry entry{
                .response = origin_resp,
                .cached_at = now,
                .max_age = std::chrono::seconds(60),
                .stale_window = std::chrono::seconds(300)
            };
            cache_->put(cache_key, std::move(entry));
            origin_resp.headers["X-Cache-Status"] = "MISS";
        } else if (cached.has_value()) {
            // Stale-if-error fallback
            auto resp = cached->response;
            resp.headers["X-Cache-Status"] = "STALE-ERROR-FALLBACK";
            return resp;
        }

        return origin_resp;
    }

private:
    HttpResponse fetch_from_origin(std::string_view url, 
                                   const std::unordered_map<std::string, std::string>& /*headers*/) {
        // Симуляція звернення до мережевого сокета пулу з'єднань
        HttpResponse resp;
        resp.status_code = 200;
        resp.headers["Content-Type"] = "application/json";
        std::string json_data = "{\"origin_data\": true, \"path\": \"" + std::string(url) + "\"}";
        resp.body.assign(json_data.begin(), json_data.end());
        return resp;
    }

    std::unique_ptr<ThreadSafeLruCache> cache_;
};

} // namespace edge
