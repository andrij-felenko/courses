#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <memory>
#include <optional>
#include <span>
#include <vector>

namespace boundary_benchmarks {

// Єдине корисне навантаження для всіх бенчмарків (ідентичний DTO)
struct RequestPayload {
    int64_t id{0};
    double value{0.0};
    char tag[16]{"bench_payload"};
};

struct ResponsePayload {
    int64_t id{0};
    double result{0.0};
    bool success{false};
};

// Базова обчислювальна логіка (однакова на всіх досліджуваних рівнях ізоляції)
inline ResponsePayload executeBusinessLogic(const RequestPayload& req) noexcept {
    return ResponsePayload{
        .id = req.id,
        .result = req.value * 2.718281828459045 + static_cast<double>(req.id),
        .success = true
    };
}

// 1. Поліморфний інтерфейс для заміру накладних витрат vtable
class ICalculator {
public:
    virtual ~ICalculator() = default;
    virtual ResponsePayload compute(const RequestPayload& req) = 0;
};

// Конкретна реалізація обчислювача
class DirectCalculator final : public ICalculator {
public:
    // Віртуальний виклик через vtable
    ResponsePayload compute(const RequestPayload& req) override;

    // Прямий машинний виклик без розіменування vtable
    ResponsePayload computeDirect(const RequestPayload& req) const noexcept;
};

// 2. Потокобезпечна черга повідомлень для міжпотокової передачі між std::jthread
template <typename T>
class ThreadSafeQueue {
public:
    ThreadSafeQueue() = default;
    ~ThreadSafeQueue() { stop(); }

    ThreadSafeQueue(const ThreadSafeQueue&) = delete;
    ThreadSafeQueue& operator=(const ThreadSafeQueue&) = delete;

    void push(T value) {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            m_queue.push(std::move(value));
        }
        m_cv.notify_one();
    }

    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_cv.wait(lock, [this] {
            return !m_queue.empty() || m_stopped.load(std::memory_order_acquire);
        });

        if (m_queue.empty()) {
            return std::nullopt;
        }

        T val = std::move(m_queue.front());
        m_queue.pop();
        return val;
    }

    void stop() {
        m_stopped.store(true, std::memory_order_release);
        m_cv.notify_all();
    }

    bool empty() const {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_queue.empty();
    }

private:
    mutable std::mutex m_mutex;
    std::queue<T> m_queue;
    std::condition_variable m_cv;
    std::atomic<bool> m_stopped{false};
};

// 3. Канал міжпроцесного зв'язку через сокети AF_UNIX
class UnixSocketChannel {
public:
    UnixSocketChannel();
    ~UnixSocketChannel();

    UnixSocketChannel(const UnixSocketChannel&) = delete;
    UnixSocketChannel& operator=(const UnixSocketChannel&) = delete;

    // Клієнтська сторона каналу
    bool sendRequest(const RequestPayload& req);
    bool receiveResponse(ResponsePayload& resp);

    // Серверна сторона каналу
    bool receiveRequest(RequestPayload& req);
    bool sendResponse(const ResponsePayload& resp);

    void close();

private:
    int m_clientFd{-1};
    int m_serverFd{-1};
    bool m_initialized{false};
};

// 4. Полегшений локальний REST-сервер та клієнт для loopback JSON викликів
class LocalRestServer {
public:
    LocalRestServer();
    ~LocalRestServer();

    LocalRestServer(const LocalRestServer&) = delete;
    LocalRestServer& operator=(const LocalRestServer&) = delete;

    void start(uint16_t port = 0);
    void stop();
    uint16_t port() const noexcept { return m_port; }

    // Відправлення HTTP POST запиту із JSON корисним навантаженням
    ResponsePayload sendHttpRequest(const RequestPayload& req);

private:
    uint16_t m_port{0};
    int m_listenFd{-1};
    std::atomic<bool> m_running{false};
    std::unique_ptr<class WorkerThread> m_worker;
};

// 5. Локальний gRPC-сервіс із двійковою серіалізацією Protobuf через HTTP/2
class LocalGrpcService {
public:
    LocalGrpcService();
    ~LocalGrpcService();

    LocalGrpcService(const LocalGrpcService&) = delete;
    LocalGrpcService& operator=(const LocalGrpcService&) = delete;

    void start();
    void stop();

    // Симуляція повного циклу gRPC виклику з двійковим кодуванням
    ResponsePayload sendRpc(const RequestPayload& req);

private:
    bool m_running{false};
    // Двійкові буфери для вимірювання витрат серіалізації Protocol Buffers
    std::vector<uint8_t> serializeProtobuf(const RequestPayload& req);
    ResponsePayload deserializeProtobuf(std::span<const uint8_t> bytes);
};

} // namespace boundary_benchmarks
