#include <string>
#include <vector>
#include <utility>
#include <concepts>

// Стани протоколу — порожні типи-маркери. Даних нема; сенс лише в імені.
struct Closed {};
struct Open   {};
struct Authed {};

// Транспорт — заглушка. У житті тут TCP-сокет, UART, TLS-сесія.
class Wire {
    std::string peer_;
    std::vector<unsigned char> inbox_;
    explicit Wire(std::string peer) : peer_(std::move(peer)) {}
public:
    static Wire dial(const std::string& peer) { return Wire{peer}; }
    void put(const std::string& bytes) { (void)bytes; /* запис у канал */ }
    std::vector<unsigned char> take() { return std::move(inbox_); }
};

// Хендл, параметризований СТАНОМ S. Стан живе лише в типі — поля під нього немає.
template <class S>
class Conn {
    Wire wire_;
    explicit Conn(Wire w) : wire_(std::move(w)) {}
    template <class> friend class Conn;   // переходи бачать приватний конструктор сусіда

public:
    Conn(const Conn&)            = delete;   // копіювати НЕ можна — інакше два живі хендли
    Conn& operator=(const Conn&) = delete;
    Conn(Conn&&)                 = default;  // переміщати — можна
    Conn& operator=(Conn&&)      = default;

    static Conn<Closed> start(const std::string& peer)
        requires std::same_as<S, Closed>
    { return Conn<Closed>{Wire::dial(peer)}; }

    // Closed → Open. `&&` — метод лише на rvalue: викликати можна тільки на
    // переміщеному (std::move) чи тимчасовому хендлі. [[nodiscard]] — новий стан не загубиш.
    [[nodiscard]] Conn<Open> open() &&
        requires std::same_as<S, Closed>
    { return Conn<Open>{std::move(wire_)}; }

    // Open → Authed. Теж &&: перехід споживає хендл.
    [[nodiscard]] Conn<Authed> authenticate(const std::string& key) &&
        requires std::same_as<S, Open>
    { wire_.put(key); return Conn<Authed>{std::move(wire_)}; }

    // ЛИШЕ у Authed. `&`, не &&: у цьому стані шлемо БАГАТО запитів, не споживаючи.
    std::vector<unsigned char> request(const std::string& body) &
        requires std::same_as<S, Authed>
    { wire_.put(body); return wire_.take(); }

    // Authed/Open → Closed. && — теж споживає.
    [[nodiscard]] Conn<Closed> close() &&
        requires (std::same_as<S, Open> || std::same_as<S, Authed>)
    { return Conn<Closed>{std::move(wire_)}; }
};
