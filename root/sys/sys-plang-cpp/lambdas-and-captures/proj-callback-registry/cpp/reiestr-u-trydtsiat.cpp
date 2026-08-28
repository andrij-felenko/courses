#include <cstddef>
#include <functional>
#include <utility>
#include <vector>

struct Tick { long long ms; double value; };

class EventBus {
public:
    using Handler = std::function<void(const Tick&)>;
    using Id = std::size_t;

    Id subscribe(Handler h) {
        const Id id = next_++;
        slots_.push_back(Slot{id, std::move(h)});
        return id;
    }

    void unsubscribe(Id id) {
        for (std::size_t i = 0; i < slots_.size(); ++i)
            if (slots_[i].id == id) { slots_.erase(slots_.begin() + i); return; }
    }

    void publish(const Tick& ev) {
        for (Slot& s : slots_) s.handler(ev);
    }

private:
    struct Slot { Id id; Handler handler; };
    std::vector<Slot> slots_;
    Id next_ = 1;
};
