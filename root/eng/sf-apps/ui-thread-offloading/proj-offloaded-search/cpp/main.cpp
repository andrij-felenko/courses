#include <atomic>
#include <condition_variable>
#include <mutex>
#include <stop_token>
#include <string>
#include <thread>
#include <variant>
#include <vector>

// ── Рівно три можливі закінчення, і тип за цим стежить ──────────────────────
struct Found     { std::vector<std::string> rows; };
struct Failed    { std::string message; };
struct Cancelled {};
using Outcome = std::variant<Found, Failed, Cancelled>;

struct Job {
    std::string     query;
    std::uint64_t   generation;   // штамп покоління
    std::stop_token stop;         // прапорець саме цього завдання
};

// ── Ворота 2: скриня на одне місце ──────────────────────────────────────────
class OneSlotMailbox {
public:
    // Кладе завдання, витісняючи те, що ще не почалося.
    void put(Job job) {
        { std::lock_guard lk(m_); slot_ = std::move(job); has_ = true; }
        cv_.notify_one();
    }

    // Чекає на завдання. false — робітника попросили спинитися.
    bool take(std::stop_token shutdown, Job& out) {
        std::unique_lock lk(m_);
        // Ця версія wait уміє прокинутися на request_stop і повертає значення
        // предиката, тобто false саме тоді, коли нас спиняють.
        if (!cv_.wait(lk, shutdown, [this] { return has_; }))
            return false;
        out = std::move(slot_);
        has_ = false;
        return true;
    }

private:
    std::mutex                  m_;
    std::condition_variable_any cv_;   // _any — бо лише він приймає stop_token
    Job                         slot_;
    bool                        has_ = false;
};

class SearchBox {
public:
    SearchBox(Index& index, UiWidgets& ui)
        : index_(index), ui_(ui),
          alive_(std::make_shared<std::atomic<bool>>(true)) {
        worker_ = std::jthread([this](std::stop_token st) { workerLoop(st); });
    }

    ~SearchBox() {
        alive_->store(false);       // усе, що вже летить назад, побачить мертвий прапорець
        debounce_.cancel();         // таймер не має тікати після смерті власника
        current_.request_stop();    // поточна робота хай вийде достроково
        worker_.request_stop();     // а цикл робітника — завершиться
    }                               // ~jthread приєднає потік сам

    // ── Викликається на потоці інтерфейсу з кожним натиском ──
    void onTextChanged(std::string text) {
        current_.request_stop();                     // те, що біжить, уже не потрібне
        // Ворота 1: кожен знак переставляє таймер спочатку
        debounce_.restart(150, [this, text = std::move(text)] {
            current_ = std::stop_source{};           // нове завдання — новий, чистий прапорець
            const std::uint64_t gen = ++generation_; // ворота 3; пише лише цей потік
            ui_.spinner.show();
            mailbox_.put(Job{ text, gen, current_.get_token() });
        });
    }

private:
    // ── Ворота 4: робота з поглядом у прапорець на межі блоку ──
    Outcome runSearch(const Job& job) {
        try {
            Found found;
            const auto& all = index_.records();
            for (std::size_t i = 0; i < all.size(); ++i) {
                if ((i & 0x1FF) == 0 && job.stop.stop_requested())
                    return Cancelled{};              // 512 — не магія, розрахунок нижче
                if (matches(all[i], job.query)) {
                    found.rows.push_back(all[i].title);
                    if (found.rows.size() == 200) break;   // більше на екран не влізе
                }
            }
            return found;
        } catch (const std::exception& e) {
            // Виняток тут нікуди не спливе: у фоновому потоці немає ані
            // обробника, ані вікна. Перетворюємо його на значення.
            return Failed{ e.what() };
        }
    }

    void workerLoop(std::stop_token shutdown) {
        Job job;
        while (mailbox_.take(shutdown, job)) {
            Outcome out = runSearch(job);
            // ── Ворота 5: маршалінг назад у чергу потоку інтерфейсу ──
            postToUiThread([this, alive = alive_, gen = job.generation,
                            out = std::move(out)]() mutable {
                if (!alive->load()) return;             // вікна вже немає — і крапка
                if (gen != generation_.load()) return;  // відповідь застаріла
                show(std::move(out));
            });
        }
    }

    void show(Outcome out) {          // потік інтерфейсу: ми знову власник дерева
        ui_.spinner.hide();
        if (auto* f = std::get_if<Found>(&out))
            ui_.list.setRows(std::move(f->rows));
        else if (auto* e = std::get_if<Failed>(&out))
            ui_.status.setText("Пошук не вдався: " + e->message);
        // Cancelled — не робимо нічого: запит скасував сам користувач
    }

    Index&         index_;
    UiWidgets&     ui_;
    UiTimer        debounce_;                     // одноразовий таймер потоку інтерфейсу
    OneSlotMailbox mailbox_;
    std::stop_source                   current_;      // прапорець поточного завдання
    std::atomic<std::uint64_t>         generation_{0};// пише інтерфейс, читає фон
    std::shared_ptr<std::atomic<bool>> alive_;        // живе довше за сам об'єкт
    std::jthread                       worker_;       // ОСТАННІМ: руйнується першим
};
