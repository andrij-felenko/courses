#include <iostream>
#include <vector>
#include <string>
#include <span>
#include <chrono>
#include <thread>
#include <future>
#include <mutex>
#include <condition_variable>
#include <expected>
#include <atomic>

struct ItemResult {
    int item_id{0};
    int price_cents{0};
};

enum class BatchError {
    NotFound,
    Timeout,
    NetworkFailure
};

struct PendingRequest {
    int item_id;
    std::promise<std::expected<ItemResult, BatchError>> promise;
};

class RemoteFacadeClient {
public:
    // Імітація одного мережевого RPC виклику до сервера
    static std::vector<std::expected<ItemResult, BatchError>>
    fetch_batch_prices(std::span<const int> item_ids) {
        // Мережевий RTT = 15 мс
        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        std::vector<std::expected<ItemResult, BatchError>> results;
        results.reserve(item_ids.size());

        for (int id : item_ids) {
            if (id <= 0) {
                results.push_back(std::unexpected(BatchError::NotFound));
            } else {
                results.push_back(ItemResult{id, id * 100 + 99});
            }
        }
        return results;
    }
};

class MicroBatcher {
public:
    explicit MicroBatcher(size_t max_batch_size = 32,
                          std::chrono::milliseconds flush_timeout = std::chrono::milliseconds(10))
        : max_batch_size_(max_batch_size),
          flush_timeout_(flush_timeout),
          running_(true),
          worker_(&MicroBatcher::worker_loop, this) {}

    ~MicroBatcher() {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            running_ = false;
        }
        cv_.notify_all();
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    // Дрібнозернистий клієнтський інтерфейс: повертає std::future для одного товару
    std::future<std::expected<ItemResult, BatchError>> get_item_price(int item_id) {
        std::promise<std::expected<ItemResult, BatchError>> prom;
        auto fut = prom.get_future();

        {
            std::unique_lock<std::mutex> lock(mutex_);
            queue_.push_back(PendingRequest{item_id, std::move(prom)});
        }
        cv_.notify_one();
        return fut;
    }

private:
    void worker_loop() {
        while (true) {
            std::vector<PendingRequest> current_batch;

            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait(lock, [this] {
                    return !running_ || !queue_.empty();
                });

                if (!running_ && queue_.empty()) {
                    break;
                }

                // Очікуємо наповнення буфера або таймауту
                cv_.wait_for(lock, flush_timeout_, [this] {
                    return queue_.size() >= max_batch_size_ || !running_;
                });

                if (queue_.empty()) {
                    continue;
                }

                size_t count = std::min(queue_.size(), max_batch_size_);
                current_batch.insert(current_batch.end(),
                                     std::make_move_iterator(queue_.begin()),
                                     std::make_move_iterator(queue_.begin() + count));
                queue_.erase(queue_.begin(), queue_.begin() + count);
            }

            if (current_batch.empty()) {
                continue;
            }

            // Формуємо список ідентифікаторів
            std::vector<int> ids;
            ids.reserve(current_batch.size());
            for (const auto& req : current_batch) {
                ids.push_back(req.item_id);
            }

            // 1 грубозернистий виклик через мережу
            auto results = RemoteFacadeClient::fetch_batch_prices(ids);

            // Демультиплексування та сповіщення конкретних потоків
            for (size_t i = 0; i < current_batch.size(); ++i) {
                current_batch[i].promise.set_value(results[i]);
            }
        }
    }

    size_t max_batch_size_;
    std::chrono::milliseconds flush_timeout_;
    std::vector<PendingRequest> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> running_;
    std::thread worker_;
};
