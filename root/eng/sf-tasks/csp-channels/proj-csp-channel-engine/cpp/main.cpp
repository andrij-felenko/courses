#include <iostream>
#include <vector>
#include <optional>
#include <mutex>
#include <condition_variable>
#include <utility>

enum class ChannelStatus {
    Success,
    Closed,
    WouldBlock
};

template <typename T>
class Channel {
public:
    explicit Channel(std::size_t capacity = 1)
        : m_capacity(std::max<std::size_t>(1, capacity)),
          m_buffer(m_capacity),
          m_head(0),
          m_tail(0),
          m_size(0),
          m_closed(false) {}

    ~Channel() {
        close();
    }

    Channel(const Channel&) = delete;
    Channel& operator=(const Channel&) = delete;
    Channel(Channel&&) = delete;
    Channel& operator=(Channel&&) = delete;

    ChannelStatus send(T value) {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_not_full.wait(lock, [this]() {
            return m_size < m_capacity || m_closed;
        });

        if (m_closed) {
            return ChannelStatus::Closed;
        }

        m_buffer[m_tail] = std::move(value);
        m_tail = (m_tail + 1) % m_capacity;
        ++m_size;

        m_not_empty.notify_one();
        return ChannelStatus::Success;
    }

    std::optional<T> recv() {
        std::unique_lock<std::mutex> lock(m_mutex);
        m_not_empty.wait(lock, [this]() {
            return m_size > 0 || m_closed;
        });

        if (m_size == 0 && m_closed) {
            return std::nullopt;
        }

        T item = std::move(m_buffer[m_head]);
        m_head = (m_head + 1) % m_capacity;
        --m_size;

        m_not_full.notify_one();
        return item;
    }

    ChannelStatus try_send(T value) {
        std::unique_lock<std::mutex> lock(m_mutex);
        if (m_closed) {
            return ChannelStatus::Closed;
        }
        if (m_size == m_capacity) {
            return ChannelStatus::WouldBlock;
        }

        m_buffer[m_tail] = std::move(value);
        m_tail = (m_tail + 1) % m_capacity;
        ++m_size;

        m_not_empty.notify_one();
        return ChannelStatus::Success;
    }

    std::pair<ChannelStatus, std::optional<T>> try_recv() {
        std::unique_lock<std::mutex> lock(m_mutex);
        if (m_size == 0) {
            if (m_closed) {
                return {ChannelStatus::Closed, std::nullopt};
            }
            return {ChannelStatus::WouldBlock, std::nullopt};
        }

        T item = std::move(m_buffer[m_head]);
        m_head = (m_head + 1) % m_capacity;
        --m_size;

        m_not_full.notify_one();
        return {ChannelStatus::Success, std::move(item)};
    }

    void close() noexcept {
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            if (m_closed) {
                return;
            }
            m_closed = true;
        }
        m_not_full.notify_all();
        m_not_empty.notify_all();
    }

    [[nodiscard]] bool is_closed() const noexcept {
        std::lock_guard<std::mutex> lock(m_mutex);
        return m_closed;
    }

private:
    const std::size_t m_capacity;
    std::vector<T> m_buffer;
    std::size_t m_head;
    std::size_t m_tail;
    std::size_t m_size;
    bool m_closed;
    mutable std::mutex m_mutex;
    std::condition_variable m_not_full;
    std::condition_variable m_not_empty;
};
