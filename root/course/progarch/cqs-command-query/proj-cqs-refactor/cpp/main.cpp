#include <atomic>
#include <cstdint>

class EventIds {
  std::atomic<std::uint64_t> next_{1};
public:
  // ВИНЯТОК: віддати поточний номер І зсунути лічильник — одним атомарним кроком
  std::uint64_t allocate() {
    return next_.fetch_add(1, std::memory_order_relaxed);  // повертає значення ДО +1
  }
};
