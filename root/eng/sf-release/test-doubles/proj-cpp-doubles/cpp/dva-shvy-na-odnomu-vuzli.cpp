#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>

struct ITransport {                                   // шов ПЕРШИЙ: інтерфейс
  virtual ~ITransport() = default;
  virtual SendStatus  send(std::span<const std::uint8_t> chunk) = 0;
  virtual std::size_t mtu() const = 0;
};

template <class Transport>                            // шов ДРУГИЙ: параметр типу
class Uplink {
 public:
  explicit Uplink(Transport& t, unsigned max_retries = 3)
      : t_(t), max_retries_(max_retries) {}

  UplinkResult sendFrame(std::span<const std::uint8_t> frame) {
    const std::size_t mtu = t_.mtu();
    for (std::size_t off = 0; off < frame.size(); ) {
      const std::size_t n = std::min(mtu, frame.size() - off);
      unsigned tries = 0;
      for (;;) {
        const SendStatus st = t_.send(frame.subspan(off, n));
        if (st == SendStatus::Ok)          break;
        if (st == SendStatus::Fatal)       return UplinkResult::Broken;
        if (++tries > max_retries_)        return UplinkResult::Congested;
      }
      off += n;
    }
    return UplinkResult::Sent;
  }

 private:
  Transport& t_;
  unsigned   max_retries_;
};
