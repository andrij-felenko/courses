// core.hpp — ядро десктопного застосунку.
// Збірка: g++ -std=c++20 -pthread   (libstdc++ від GCC 12.1 і новіше)
#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <functional>
#include <memory>
#include <mutex>
#include <stop_token>
#include <string>
#include <string_view>
#include <thread>
#include <utility>
#include <vector>

// ─── 1. Стан: документ незмінний, версії публікують цілими ──────────────────
struct Document {
    std::string              text;
    std::vector<std::string> matches;
};
using Snapshot = std::shared_ptr<const Document>;

class Model {
public:
    Snapshot snapshot() const { return state_.load(std::memory_order_acquire); }
    void publish(Snapshot next) { state_.store(std::move(next), std::memory_order_release); }

private:
    std::atomic<Snapshot> state_{std::make_shared<const Document>()};
};

// ─── 2. Черга відкладених викликів у потік інтерфейсу ───────────────────────
class UiQueue {
public:
    explicit UiQueue(std::size_t cap) : cap_(cap) {}

    bool post(std::function<void()> call) {              // з БУДЬ-ЯКОГО потоку
        {
            std::lock_guard lk(m_);
            if (closed_ || q_.size() >= cap_) { ++refused_; return false; }
            q_.push_back(std::move(call));
        }
        cv_.notify_one();
        return true;
    }

    void run() {                                         // ЛИШЕ потік інтерфейсу
        for (;;) {
            std::deque<std::function<void()>> batch;
            {
                std::unique_lock lk(m_);
                cv_.wait(lk, [&] { return !q_.empty() || closed_; });
                if (q_.empty()) return;                  // закрито й порожньо — виходимо
                batch.swap(q_);                          // забрали пачку — замок віддали
            }
            for (auto& call : batch) call();             // ← виклики ПОЗА замком
        }
    }

    void close() {
        { std::lock_guard lk(m_); closed_ = true; }
        cv_.notify_all();
    }

    std::size_t refused() const { std::lock_guard lk(m_); return refused_; }

private:
    mutable std::mutex                m_;
    std::condition_variable           cv_;
    std::deque<std::function<void()>> q_;
    std::size_t cap_;
    std::size_t refused_ = 0;
    bool        closed_  = false;
};

// ─── 3. Пул виконавців ──────────────────────────────────────────────────────
class Pool {
public:
    explicit Pool(unsigned n) {
        workers_.reserve(n);
        for (unsigned i = 0; i < n; ++i) workers_.emplace_back([this] { loop(); });
    }
    ~Pool() { close(); }        // тіло — ДО знищення полів; далі workers_ гине першим

    bool submit(std::function<void()> job) {
        {
            std::lock_guard lk(m_);
            if (closed_) return false;
            jobs_.push_back(std::move(job));
        }
        cv_.notify_one();
        return true;
    }

    void close() {
        { std::lock_guard lk(m_); closed_ = true; }
        cv_.notify_all();
    }

private:
    void loop() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock lk(m_);
                cv_.wait(lk, [&] { return !jobs_.empty() || closed_; });
                if (closed_) return;                     // недороблене кидаємо свідомо
                job = std::move(jobs_.front());
                jobs_.pop_front();
            }
            try { job(); } catch (...) {}                // виняток звідси = std::terminate
        }
    }

    std::mutex                        m_;
    std::condition_variable           cv_;
    std::deque<std::function<void()>> jobs_;
    bool                              closed_ = false;
    std::vector<std::jthread>         workers_;   // ОСТАННЄ поле → гине ПЕРШИМ
};

// ─── 4. Застосунок: покоління, скасування, публікація ───────────────────────
class App {
public:
    void run() { ui_.run(); }

    // ↓↓↓ усе нижче викликають ЛИШЕ з потоку інтерфейсу ↓↓↓
    void on_query_changed(std::string query) {
        inflight_.request_stop();                        // попереднє питання зняте
        inflight_ = std::stop_source{};                  // нове питання — новий токен
        unsigned        gen  = ++gen_;                   // звичайний int: потік один
        std::stop_token stop = inflight_.get_token();
        Snapshot        base = model_.snapshot();        // вхід — незмінний знімок

        pool_.submit([this, query = std::move(query), base, gen, stop] {
            std::vector<std::string> found = grep(base->text, query, stop);
            if (stop.stop_requested()) return;           // економія: не турбуємо інтерфейс
            ui_.post([this, base, gen, found = std::move(found)]() mutable {
                if (gen != gen_) return;                 // коректність: відповідь застаріла
                auto next = std::make_shared<Document>(*base);
                next->matches = std::move(found);
                model_.publish(std::move(next));         // публікація — один запис
                repaint();
            });
        });
    }

    void on_close() {
        inflight_.request_stop();   // 1. попросити те, що в польоті, згорнутися
        pool_.close();              // 2. нових завдань не приймати
        ui_.close();                // 3. цикл добіжить і поверне з run()
    }

private:
    static std::vector<std::string> grep(const std::string& text, const std::string& needle,
                                         const std::stop_token& stop) {
        std::vector<std::string> out;
        if (needle.empty()) return out;
        std::size_t from = 0, line = 0;
        for (std::size_t i = 0; i <= text.size(); ++i) {
            if (i != text.size() && text[i] != '\n') continue;
            if ((++line & 0xFF) == 0 && stop.stop_requested()) return {};   // безпечна точка
            std::string_view row(text.data() + from, i - from);
            if (row.find(needle) != std::string_view::npos) out.emplace_back(row);
            from = i + 1;
        }
        return out;
    }

    void repaint() {                        // потік інтерфейсу, замків нуль
        Snapshot s = model_.snapshot();
        draw(*s);                           // s тримає версію живою, доки ми малюємо
    }
    static void draw(const Document&) { /* виклики тулкіта */ }

    Model            model_;
    unsigned         gen_ = 0;
    std::stop_source inflight_;
    UiQueue          ui_{1024};     // гине ДРУГИМ
    Pool             pool_{4};      // гине ПЕРШИМ: приєднає потоки, поки черги ще живі
};
