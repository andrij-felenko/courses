#include <cstdio>
#include <deque>
#include <memory>
#include <string>
#include <variant>
#include <vector>

// ── Стан: усе, що застосунок пам'ятає між подіями ────────────────────────
enum class Field { Usd, Eur };

struct State {
    Field       entered = Field::Usd;  // яке поле набрала людина
    long long   amount  = 0;           // набране число в сотих (центах)
    long long   rate    = 92;          // курс у сотих: 0.92 євро за долар
    bool        pending = false;       // запит курсу вже в дорозі
    std::string note;                  // рядок для людини
};

// ── Дії: описи того, що сталося. Самі нічого не роблять ──────────────────
struct Typed      { Field field; long long amount; };
struct RateAsked  { };
struct RateCame   { long long rate; };
struct RateFailed { std::string why; };

using Action = std::variant<Typed, RateAsked, RateCame, RateFailed>;

// ── Ефекти: описи того, що має зробити оболонка ──────────────────────────
struct FetchRate { };
struct Persist   { };
struct Retry     { int after_ms; };

using Effect = std::variant<FetchRate, Persist, Retry>;
