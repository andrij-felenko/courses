#include <deque>

class FakeTransport {
 public:
  FakeTransport(std::size_t mtu, std::size_t capacity)
      : mtu_(mtu), capacity_(capacity) {}

  // ── поверхня контракту: рівно те, що бачить Uplink ──
  std::size_t mtu() const { return mtu_; }

  SendStatus send(std::span<const std::uint8_t> chunk) {
    if (chunk.size() > mtu_)            return SendStatus::Fatal;
    if (queue_.size() >= capacity_)     return SendStatus::WouldBlock;
    queue_.emplace_back(chunk.begin(), chunk.end());
    return SendStatus::Ok;
  }

  // ── вікно тесту: цього в контракті НЕМАЄ ──
  std::size_t queued() const { return queue_.size(); }
  std::vector<std::uint8_t> drainOne() {
    auto front = std::move(queue_.front());
    queue_.pop_front();
    return front;
  }

 private:
  std::size_t mtu_, capacity_;
  std::deque<std::vector<std::uint8_t>> queue_;
};
