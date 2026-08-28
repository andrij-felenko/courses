using clk = std::chrono::steady_clock;
using ms  = std::chrono::milliseconds;

constexpr ms T1{500};              // оцінка часу обігу за замовчуванням
constexpr ms TIMER_B  = 64 * T1;   // 32 с — стеля мовчання
constexpr ms TIMER_D{32000};       // ≥ 32 с — поглинання дублів
constexpr ms RINGING{180000};      // власна межа для Proceeding (див. пастку 1)
constexpr auto NEVER = clk::time_point::max();

enum class St : uint8_t { Calling, Proceeding, Completed };

struct Txn {
    St        st       = St::Calling;
    clk::time_point a  = NEVER;    // наступний повтор
    clk::time_point bd = NEVER;    // здача (B) або кінець поглинання (D)
    ms        step     = T1;       // поточний крок повтору
    uint64_t  key      = 0;        // branch ⊕ метод CSeq
    uint16_t  len      = 0;
    char      req[1400];           // серіалізовано ОДИН раз: повтори йдуть байт-у-байт
};

// Дає парсер (поза цим прикладом): вказівники всередину буфера прийому.
struct Match { std::string_view branch, method; int status; };
Match parse(std::string_view msg) noexcept;

class TxnLayer {
public:
    TxnLayer(Udp& u, Tu& tu) : udp_(u), tu_(tu) {
        pool_.resize(kMax);                 // єдині алокації — на старті
        index_.reserve(kMax * 2);
        for (uint32_t i = kMax; i-- > 0;) free_.push_back(i);
    }

    uint32_t start(std::string_view invite, clk::time_point now) {
        uint32_t i = free_.back(); free_.pop_back();
        Txn& t = pool_[i];
        t = Txn{};
        t.step = T1;
        t.a    = now + T1;                  // таймер A
        t.bd   = now + TIMER_B;             // таймер B
        t.len  = pack(t.req, invite);
        t.key  = key_of(top_via_branch(invite), "INVITE");
        index_.emplace(t.key, i);
        udp_.send(t.req, t.len);
        return i;
    }

    // Гарячий шлях: прийшов пакет. Жодної алокації, жодного копіювання тіла.
    void on_response(std::string_view msg, clk::time_point now) {
        const Match m = parse(msg);
        auto it = index_.find(key_of(m.branch, m.method));
        if (it == index_.end()) { tu_.stray(msg); return; }   // не наша — нагору як є
        Txn& t = pool_[it->second];

        if (m.status < 200) {                       // 1xx
            if (t.st == St::Calling) {
                t.st = St::Proceeding;
                t.a  = NEVER;                       // повтори спиняємо
                t.bd = now + RINGING;               // і міняємо межу очікування
            }
            tu_.provisional(it->second, msg);
        } else if (m.status < 300) {                // 2xx
            tu_.success(it->second, msg);           // ACK зробить TU, не ми
            release(it);                            // транзакція гине негайно
        } else {                                    // 300–699
            send_ack(t, m);                         // ACK наш, із тим самим branch
            if (t.st != St::Completed) {            // доповідаємо РІВНО раз
                tu_.failure(it->second, msg);
                t.st = St::Completed;
                t.a  = NEVER;
                t.bd = now + TIMER_D;               // далі лише мовчки ACK-аємо дублі
            }
        }
    }

    void tick(clk::time_point now) {
        for (auto it = index_.begin(); it != index_.end(); ) {
            Txn& t = pool_[it->second];
            if (now >= t.a) {
                udp_.send(t.req, t.len);            // той самий байт-у-байт запит
                t.step *= 2;                        // 0.5 → 1 → 2 → 4 … без стелі T2
                t.a = now + t.step;
            }
            if (now >= t.bd) {
                if (t.st != St::Completed) tu_.timeout(it->second);  // ACK тут НЕ шлемо
                release(it++);
                continue;
            }
            ++it;
        }
    }

private:
    // Єдине місце, де транзакція вмирає. Обидва таймери зникають разом
    // із записом — осиротілий таймер, що стрельне в мертву транзакцію,
    // у цій схемі неможливий.
    void release(Index::iterator it) noexcept {
        free_.push_back(it->second);
        index_.erase(it);
    }

    static constexpr uint32_t kMax = 8192;
    Udp& udp_; Tu& tu_;
    std::vector<Txn>     pool_;
    std::vector<uint32_t> free_;
    Index                index_;   // unordered_map<uint64_t, uint32_t>
};
