class TileScheduler {
public:
    struct Flight {
        explicit Flight(uint64_t g) : startGeneration(g) {}
        uint64_t            startGeneration;
        std::atomic<bool>   abort{false};
        std::atomic<size_t> bytesReceived{0};
    };
    using FlightPtr = std::shared_ptr<Flight>;

    explicit TileScheduler(size_t maxInFlight) : maxInFlight_(maxInFlight) {}

    // ── Потік малювання ───────────────────────────────────────────────────
    // Нове покоління: усе, що чекало, більше не описує екран. Гуртом за борт.
    void newGeneration(uint64_t g) {
        {
            std::lock_guard<std::mutex> lock(m_);
            generation_ = g;
            heap_ = Heap{};        // у std::priority_queue немає clear()
            pending_.clear();      // те, що ще потрібне, цей же кадр покладе знову
        }
        cv_.notify_all();
    }

    void request(const TileId& id, const Viewport& vp) {
        {
            std::lock_guard<std::mutex> lock(m_);
            if (vp.generation != generation_) return;   // кадр спізнився — його потреба не наша
            if (inFlight_.count(id)) return;            // уже летить — мовчки приєдналися
            if (!pending_.insert(id).second) return;    // уже в купі цього покоління
            heap_.push(Request{ id, vp.generation,
                                std::abs(vp.zoom - id.z), dist2(id, vp) });
        }
        cv_.notify_one();
    }

    // ── Фонові потоки ─────────────────────────────────────────────────────
    // Блокується, доки не з'явиться робота або доки не скажуть спинитися.
    bool take(Request& out, FlightPtr& flight) {
        std::unique_lock<std::mutex> lock(m_);
        for (;;) {
            if (!heap_.empty() && inFlight_.size() < maxInFlight_) {
                const Request r = heap_.top();
                heap_.pop();
                pending_.erase(r.id);
                assert(r.generation == generation_);   // купу чистять на зміні покоління
                flight = std::make_shared<Flight>(r.generation);
                inFlight_.emplace(r.id, flight);
                out = r;
                return true;
            }
            if (stop_) return false;
            cv_.wait(lock);
        }
    }

    // Стирання запису про політ — робота ДЕСТРУКТОРА, а не щасливого шляху.
    class FlightGuard {
    public:
        FlightGuard(TileScheduler& s, TileId id) : s_(s), id_(id) {}
        ~FlightGuard() { s_.retire(id_); }
        FlightGuard(const FlightGuard&) = delete;
        FlightGuard& operator=(const FlightGuard&) = delete;
    private:
        TileScheduler& s_;
        TileId id_;
    };

    void retire(const TileId& id) {
        {
            std::lock_guard<std::mutex> lock(m_);
            inFlight_.erase(id);
        }
        cv_.notify_all();
    }

    // Скасувати в польоті можна ЛИШЕ те, що ще не прийняло жодного байта,
    // і лише коли всі з'єднання зайняті, а в купі чекає свіжий запит.
    void reclaimSlot() {
        std::lock_guard<std::mutex> lock(m_);
        if (heap_.empty() || inFlight_.size() < maxInFlight_) return;
        for (auto& [id, f] : inFlight_) {
            if (f->startGeneration == generation_) continue;                  // актуальний
            if (f->bytesReceived.load(std::memory_order_relaxed) != 0) continue;  // вже платимо
            f->abort.store(true, std::memory_order_relaxed);
            return;                                                           // одне з'єднання за раз
        }
    }

    void stop() {
        { std::lock_guard<std::mutex> lock(m_); stop_ = true; }
        cv_.notify_all();
    }

private:
    using Heap = std::priority_queue<Request, std::vector<Request>, Worse>;

    std::mutex              m_;
    std::condition_variable cv_;
    Heap                    heap_;
    std::unordered_set<TileId, TileHash>            pending_;
    std::unordered_map<TileId, FlightPtr, TileHash> inFlight_;
    uint64_t generation_ = 0;
    size_t   maxInFlight_;
    bool     stop_ = false;
};
