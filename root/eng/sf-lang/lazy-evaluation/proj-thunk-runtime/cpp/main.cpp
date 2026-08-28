#include <iostream>
#include <memory>
#include <functional>
#include <stdexcept>
#include <variant>

// Виняток для детекції нескінченних циклів
class BottomLoopException : public std::runtime_error {
public:
    BottomLoopException() : std::runtime_error("<<loop>>: виявлено пряму циклічну залежність санка!") {}
};

// Узагальнений клас санка
template <typename T>
class Thunk : public std::enable_shared_from_this<Thunk<T>> {
private:
    struct Blackhole {};
    using State = std::variant<std::function<T()>, Blackhole, T>;
    mutable State state_;

public:
    // Конструктор від відкладеного обчислення (лямбди)
    explicit Thunk(std::function<T()> compute_fn)
        : state_(std::move(compute_fn)) {}

    // Конструктор від уже готового значення
    explicit Thunk(T val)
        : state_(std::move(val)) {}

    // Фабричні методи
    static std::shared_ptr<Thunk<T>> delay(std::function<T()> fn) {
        return std::make_shared<Thunk<T>>(std::move(fn));
    }

    static std::shared_ptr<Thunk<T>> value(T val) {
        return std::make_shared<Thunk<T>>(std::move(val));
    }

    // Форсування санка
    const T& force() const {
        if (std::holds_alternative<T>(state_)) {
            return std::get<T>(state_);
        }

        if (std::holds_alternative<Blackhole>(state_)) {
            throw BottomLoopException();
        }

        // Перехід у стан Blackhole
        auto compute_fn = std::move(std::get<std::function<T()>>(state_));
        state_ = Blackhole{};

        // Виконання обчислення та мутація вузла на місці
        T result = compute_fn();
        state_ = std::move(result);

        return std::get<T>(state_);
    }

    bool is_evaluated() const noexcept {
        return std::holds_alternative<T>(state_);
    }
};

// Допоміжний синтаксис
template <typename T>
const T& force(const std::shared_ptr<Thunk<T>>& thunk) {
    return thunk->force();
}

// --- Лінивий нескінченний потік мовою C++ ---
template <typename T>
struct StreamNode {
    T head;
    std::shared_ptr<Thunk<StreamNode<T>>> tail;
};

template <typename T>
using LazyStream = std::shared_ptr<Thunk<StreamNode<T>>>;

static size_t g_cpp_eval_count = 0;

// Генератор чисел Фібоначчі
LazyStream<long long> make_fib_stream(long long a = 0, long long b = 1) {
    return Thunk<StreamNode<long long>>::delay([a, b]() {
        g_cpp_eval_count++;
        return StreamNode<long long>{
            a,
            make_fib_stream(b, a + b)
        };
    });
}

// Друк перших N елементів
template <typename T>
void print_take(LazyStream<T> stream, size_t n) {
    std::cout << "Перші " << n << " елементів: [";
    auto current = stream;
    for (size_t i = 0; i < n; ++i) {
        const auto& node = force(current);
        std::cout << node.head << (i + 1 < n ? ", " : "");
        current = node.tail;
    }
    std::cout << "]\n";
}

int main() {
    std::cout << "=== Демонстрація рушія санків на C++ ===\n";

    // 1. Створюємо нескінченний потік
    auto fibs = make_fib_stream(0, 1);

    // 2. Беремо 10 чисел
    print_take(fibs, 10);
    std::cout << "Кількість викликів лямбди: " << g_cpp_eval_count << " (точно 10)\n";

    // 3. Перевірка кешування: беремо 5 чисел з того самого об'єкта
    size_t prev = g_cpp_eval_count;
    print_take(fibs, 5);
    std::cout << "Нових обчислень для перших 5 чисел: " << (g_cpp_eval_count - prev) << " (0 нових!)\n";

    // 4. Демонстрація перехоплення Blackhole при зацикленні: let x = x + 1
    std::shared_ptr<Thunk<int>> cyclic_thunk;
    cyclic_thunk = Thunk<int>::delay([&cyclic_thunk]() {
        return cyclic_thunk->force() + 1;
    });

    try {
        std::cout << "Спроба форсувати циклічний санк: ";
        cyclic_thunk->force();
    } catch (const BottomLoopException& e) {
        std::cout << "УСПІШНО ПЕРЕХОПЛЕНО -> " << e.what() << "\n";
    }

    return 0;
}
