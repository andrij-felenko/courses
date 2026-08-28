#include <deque>
#include <optional>
#include <functional>
#include <chrono>

struct Selection {                 // де стояла увага людини
    std::string nodeId;            // ЩО виділено — стабільний id, а не «третій згори»
    int from = 0, to = 0;          // діапазон усередині тексту вузла
};

// Результат правки: нова версія + скільки байтів правка ВИЛУЧИЛА з дерева.
struct EditResult { NodeP root; std::size_t removed = 0; };
using Edit = std::function<EditResult(const NodeP&)>;   // чиста функція: стара версія → нова

struct Step {
    NodeP       before, after;      // два кореня — два вказівники, не дві копії
    Selection   selBefore, selAfter;
    std::string label;              // «набір тексту» — те, що стане в меню «Скасувати …»
    std::string mergeKey;           // порожній ⇒ із сусіднім кроком не зливати
    std::size_t weight = 0;         // додане + вилучене цим кроком, у байтах
    std::chrono::steady_clock::time_point at;
};

class Store {
public:
    Store(NodeP root, std::size_t budget, std::function<void()> onChange)
        : root_(std::move(root)), budget_(budget), notify_(std::move(onChange)) {}

    const NodeP&     doc()       const { return root_; }
    const Selection& selection() const { return sel_; }

    void apply(const Edit& edit, Selection selAfter);        // ЄДИНА точка зміни моделі
    void begin(std::string label, std::string mergeKey = {});
    void commit();
    void rollback() noexcept;

    bool undo();
    bool redo();
    void markSaved()      { saved_ = static_cast<long long>(index_); }
    bool isDirty()  const { return saved_ != static_cast<long long>(index_); }

private:
    struct Open {                       // відкрита транзакція
        NodeP       base;               // корінь на початку наміру
        Selection   selBefore;
        std::string label, mergeKey;
        std::size_t born0 = 0;          // g_born на початку
        std::size_t removed = 0;
    };
    void pushStep(Step st);
    void trim();
    void retire(Step dead);             // віддати мертвий крок прибиральникові

    NodeP                 root_;        // ← ЄДИНА змінна комірка в усьому сховищі
    Selection             sel_;
    std::deque<Step>      steps_;       // deque: викидаємо і з кінця, і з ДНА
    std::size_t           index_ = 0;   // скільки кроків застосовано (курсор на лінії)
    long long             saved_ = 0;   // −1 ⇒ збережений стан недосяжний
    std::size_t           bytes_ = 0;   // Σ ваг кроків
    std::size_t           budget_;
    std::optional<Open>   open_;
    std::function<void()> notify_;
    Disposer              disposer_;    // фоновий прибиральник; його визначення — наприкінці
};
