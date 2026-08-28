// C++: Ідіоматична потокобезпечна реалізація DataLoader на базі std::future та RAII

#include <iostream>
#include <vector>
#include <unordered_map>
#include <memory>
#include <future>
#include <functional>
#include <mutex>
#include <stdexcept>
#include <string>

template <typename Key, typename Value>
class DataLoader {
public:
    using BatchFunction = std::function<std::vector<Value>(const std::vector<Key>&)>;

    explicit DataLoader(BatchFunction batchFn, size_t maxBatchSize = 1000)
        : batchFn_(std::move(batchFn)), maxBatchSize_(maxBatchSize) {}

    // Метод load реєструє ключ і повертає std::shared_future на майбутній результат
    std::shared_future<Value> load(const Key& key) {
        std::lock_guard<std::mutex> lock(mutex_);

        // 1. Перевіряємо наявність у кеші
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second;
        }

        // 2. Створюємо новий promise для асинхронного результату
        auto promisePtr = std::make_shared<std::promise<Value>>();
        std::shared_future<Value> future = promisePtr->get_future().share();
        cache_.emplace(key, future);

        queue_.push_back({key, promisePtr});

        return future;
    }

    // Скидання черги: виконання пакетного запиту для всіх накопичених ключів
    void dispatch() {
        std::vector<QueueItem> currentQueue;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (queue_.empty()) return;
            currentQueue = std::move(queue_);
            queue_.clear();
        }

        std::vector<Key> keys;
        keys.reserve(currentQueue.size());
        for (const auto& item : currentQueue) {
            keys.push_back(item.key);
        }

        try {
            // Виклик користувацької пакетної функції
            std::vector<Value> results = batchFn_(keys);

            if (results.size() != keys.size()) {
                throw std::runtime_error(
                    "DataLoader batch function returned vector of incorrect size: expected " +
                    std::to_string(keys.size()) + ", got " + std::to_string(results.size())
                );
            }

            // Розподіл результатів по promise
            for (size_t i = 0; i < currentQueue.size(); ++i) {
                currentQueue[i].promise->set_value(results[i]);
            }
        } catch (...) {
            auto ex = std::current_exception();
            for (auto& item : currentQueue) {
                item.promise->set_exception(ex);
            }
        }
    }

    void clear(const Key& key) {
        std::lock_guard<std::mutex> lock(mutex_);
        cache_.erase(key);
    }

    void clearAll() {
        std::lock_guard<std::mutex> lock(mutex_);
        cache_.clear();
    }

private:
    struct QueueItem {
        Key key;
        std::shared_ptr<std::promise<Value>> promise;
    };

    BatchFunction batchFn_;
    size_t maxBatchSize_;
    std::mutex mutex_;
    std::vector<QueueItem> queue_;
    std::unordered_map<Key, std::shared_future<Value>> cache_;
};
