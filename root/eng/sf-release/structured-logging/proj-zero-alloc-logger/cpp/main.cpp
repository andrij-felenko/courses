#include <iostream>
#include <string_view>
#include <array>
#include <atomic>
#include <thread>
#include <chrono>
#include <cstring>
#include <cstdint>

#if defined(_WIN32)
  #include <io.h>
  #define WRITE_STDOUT(buf, len) _write(1, buf, static_cast<unsigned int>(len))
#else
  #include <unistd.h>
  #define WRITE_STDOUT(buf, len) write(STDOUT_FILENO, buf, len)
#endif

// Конфігураційні константи
constexpr size_t MAX_MSG_SIZE = 512;
constexpr size_t RING_SLOTS   = 4096; // Степінь двійки
constexpr size_t RING_MASK    = RING_SLOTS - 1;

enum class LogLevel : uint8_t {
    Debug,
    Info,
    Warn,
    Error
};

constexpr std::string_view LevelToString(LogLevel lvl) noexcept {
    switch (lvl) {
        case LogLevel::Debug: return "DEBUG";
        case LogLevel::Info:  return "INFO";
        case LogLevel::Warn:  return "WARN";
        case LogLevel::Error: return "ERROR";
    }
    return "UNKNOWN";
}

// Слот для збереження однієї серіалізованої події у черзі
struct alignas(64) LogSlot {
    uint16_t length{0};
    char data[MAX_MSG_SIZE];
};

// Стек-орієнтований JSON-кодер без виділення пам'яті на купі
class FastJsonWriter {
public:
    explicit FastJsonWriter(char* target, size_t capacity) noexcept
        : buf_(target), cap_(capacity), pos_(0) {
        if (cap_ > 0) {
            buf_[0] = '{';
            pos_ = 1;
        }
    }

    void AddString(std::string_view key, std::string_view val) noexcept {
        PrepareKey(key);
        AppendChar('"');
        for (char c : val) {
            if (c == '"' || c == '\\') {
                AppendChar('\\');
            }
            AppendChar(c);
        }
        AppendChar('"');
    }

    void AddInt(std::string_view key, int64_t val) noexcept {
        PrepareKey(key);
        if (val < 0) {
            AppendChar('-');
            val = -val;
        }
        FormatUint(static_cast<uint64_t>(val));
    }

    void AddBool(std::string_view key, bool val) noexcept {
        PrepareKey(key);
        if (val) {
            AppendBytes("true", 4);
        } else {
            AppendBytes("false", 5);
        }
    }

    size_t Finish() noexcept {
        if (pos_ + 2 <= cap_) {
            buf_[pos_++] = '}';
            buf_[pos_++] = '\n';
        }
        return pos_;
    }

private:
    char*  buf_;
    size_t cap_;
    size_t pos_;
    bool   has_fields_{false};

    void PrepareKey(std::string_view key) noexcept {
        if (has_fields_) {
            AppendChar(',');
        }
        has_fields_ = true;
        AppendChar('"');
        AppendBytes(key.data(), key.size());
        AppendChar('"');
        AppendChar(':');
    }

    void AppendChar(char c) noexcept {
        if (pos_ < cap_) {
            buf_[pos_++] = c;
        }
    }

    void AppendBytes(const char* src, size_t len) noexcept {
        if (pos_ + len <= cap_) {
            std::memcpy(buf_ + pos_, src, len);
            pos_ += len;
        }
    }

    void FormatUint(uint64_t v) noexcept {
        char tmp[24];
        int tp = 0;
        if (v == 0) {
            AppendChar('0');
            return;
        }
        while (v > 0) {
            tmp[tp++] = static_cast<char>('0' + (v % 10));
            v /= 10;
        }
        while (tp > 0) {
            AppendChar(tmp[--tp]);
        }
    }
};

// Беззамковий кільцевий буфер з атомарними покажчиками
class LockFreeLogRing {
public:
    LockFreeLogRing() noexcept = default;

    bool TryPush(const char* data, size_t len) noexcept {
        if (len > MAX_MSG_SIZE) return false;

        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_acquire);

        // Перевірка на заповненість буфера
        if ((head - tail) >= RING_SLOTS) {
            dropped_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        const size_t idx = head & RING_MASK;
        std::memcpy(slots_[idx].data, data, len);
        slots_[idx].length = static_cast<uint16_t>(len);

        // Публікація індексу: споживач бачить дані лише після цього запису
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

    bool TryPop(char* out_data, size_t& out_len) noexcept {
        const size_t tail = tail_.load(std::memory_order_relaxed);
        const size_t head = head_.load(std::memory_order_acquire);

        if (tail == head) {
            return false; // Буфер порожній
        }

        const size_t idx = tail & RING_MASK;
        out_len = slots_[idx].length;
        std::memcpy(out_data, slots_[idx].data, out_len);

        tail_.store(tail + 1, std::memory_order_release);
        return true;
    }

    uint64_t Dropped() const noexcept {
        return dropped_count_.load(std::memory_order_relaxed);
    }

private:
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};
    alignas(64) std::atomic<uint64_t> dropped_count_{0};
    std::array<LogSlot, RING_SLOTS> slots_{};
};

// Головний фасад асинхронного логера
class AsyncLogger {
public:
    AsyncLogger() : running_(true), worker_(&AsyncLogger::FlushLoop, this) {}

    ~AsyncLogger() {
        running_.store(false, std::memory_order_release);
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    void Log(LogLevel lvl, std::string_view msg, int64_t user_id, int64_t duration_ms) noexcept {
        char local_buf[MAX_MSG_SIZE];
        FastJsonWriter writer(local_buf, sizeof(local_buf));

        writer.AddString("level", LevelToString(lvl));
        writer.AddString("msg", msg);
        writer.AddInt("user_id", user_id);
        writer.AddInt("duration_ms", duration_ms);

        size_t len = writer.Finish();
        ring_.TryPush(local_buf, len);
    }

private:
    LockFreeLogRing    ring_;
    std::atomic<bool>  running_{false};
    std::thread        worker_;

    void FlushLoop() noexcept {
        char batch_buf[MAX_MSG_SIZE * 32];
        size_t batch_len = 0;
        char item_buf[MAX_MSG_SIZE];
        size_t item_len = 0;

        while (running_.load(std::memory_order_acquire)) {
            bool found_any = false;
            while (ring_.TryPop(item_buf, item_len)) {
                found_any = true;
                if (batch_len + item_len > sizeof(batch_buf)) {
                    WRITE_STDOUT(batch_buf, batch_len);
                    batch_len = 0;
                }
                std::memcpy(batch_buf + batch_len, item_buf, item_len);
                batch_len += item_len;
            }

            if (batch_len > 0) {
                WRITE_STDOUT(batch_buf, batch_len);
                batch_len = 0;
            }

            if (!found_any) {
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
        }

        // Завершальний скид усіх залишків перед зупинкою
        while (ring_.TryPop(item_buf, item_len)) {
            if (batch_len + item_len > sizeof(batch_buf)) {
                WRITE_STDOUT(batch_buf, batch_len);
                batch_len = 0;
            }
            std::memcpy(batch_buf + batch_len, item_buf, item_len);
            batch_len += item_len;
        }
        if (batch_len > 0) {
            WRITE_STDOUT(batch_buf, batch_len);
        }
    }
};

int main() {
    AsyncLogger logger;
    logger.Log(LogLevel::Info, "order_created", 84920, 14);
    logger.Log(LogLevel::Error, "payment_timeout", 84920, 3004);

    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    return 0;
}
