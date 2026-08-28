#include <atomic>
#include <chrono>
#include <cstdint>
#include <optional>
#include <queue>
#include <shared_mutex>
#include <string>
#include <unordered_map>
#include <vector>

using Clock     = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using Duration  = Clock::duration;
using Key       = std::string;

struct Payload {                 // те, заради чого запис існує
    std::string address;
    uint16_t    port = 0;
    uint32_t    load = 0;
};

struct Entry {
    Payload   payload;
    uint64_t  incarnation = 0;   // покоління відправника: зростає з кожним стартом процесу
    uint64_t  epoch       = 0;   // номер вставки в таблицю: відсіює осиротілі вузлики купи
    TimePoint deadline{};        // момент смерті, порахований ПРИЙМАЧЕМ
    TimePoint expired_at{};      // коли строк минув; має сенс лише для підозрюваних
    bool      live = true;
};

struct Event {                   // вузлик купи: рівно один на кожен запис
    TimePoint when;
    Key       key;
    uint64_t  epoch;
};

struct Later {                   // мінімум зверху
    bool operator()(const Event& a, const Event& b) const { return a.when > b.when; }
};

class Registry {
public:
    Registry(Duration lifetime, Duration grace, Duration hard_grace, unsigned panic_pct)
        : lifetime_(lifetime), grace_(grace), hard_grace_(hard_grace), panic_pct_(panic_pct) {}

    // ── ГАРЯЧИЙ ШЛЯХ: N/T разів за секунду. Купи не торкається.
    bool on_refresh(const Key& k, uint64_t incarnation, Payload p) {
        const TimePoint deadline = Clock::now() + lifetime_;   // строк рахує приймач

        std::unique_lock<std::shared_mutex> g(mu_);
        auto it = table_.find(k);
        if (it == table_.end()) {
            Entry e;
            e.payload     = std::move(p);
            e.incarnation = incarnation;
            e.epoch       = ++epoch_seq_;
            e.deadline    = deadline;
            table_.emplace(k, std::move(e));
            heap_.push(Event{deadline, k, epoch_seq_});        // єдиний дотик до купи
            ++live_;
            return true;
        }

        Entry& e = it->second;
        if (incarnation < e.incarnation) return false;         // луна минулого життя
        e.incarnation = incarnation;                           // нове втілення нічого не успадковує
        e.payload     = std::move(p);
        e.deadline    = deadline;                              // єдине, що робить оновлення
        if (!e.live) { e.live = true; ++live_; }               // підозрюваний повернувся
        return true;
    }

    struct View { Payload payload; bool fresh; };

    // ── Читання: під спільним замком, ЗАВЖДИ копією.
    std::optional<View> lookup(const Key& k) const {
        const TimePoint now = Clock::now();
        std::shared_lock<std::shared_mutex> g(mu_);
        auto it = table_.find(k);
        if (it == table_.end()) return std::nullopt;
        const bool fresh = it->second.deadline > now;
        if (!fresh && !panic_) return std::nullopt;            // строк минув, і ми собі віримо
        return View{it->second.payload, fresh};
    }

    // ── Явне «я йду»: підказка для швидкості, не несуча конструкція.
    void withdraw(const Key& k, uint64_t incarnation) {
        Entry corpse;                                          // оголошено ДО замка — див. sweep()
        std::unique_lock<std::shared_mutex> g(mu_);
        auto it = table_.find(k);
        if (it == table_.end() || incarnation < it->second.incarnation) return;
        if (it->second.live) --live_;
        corpse = std::move(it->second);
        table_.erase(it);
    }

private:
    mutable std::shared_mutex                              mu_;
    std::unordered_map<Key, Entry>                         table_;
    std::priority_queue<Event, std::vector<Event>, Later>  heap_;
    size_t   live_      = 0;      // скільки записів у таблиці зараз живі
    uint64_t epoch_seq_ = 0;
    bool     panic_     = false;
    const Duration lifetime_, grace_, hard_grace_;
    const unsigned panic_pct_;

    // ...sweep() нижче
};
