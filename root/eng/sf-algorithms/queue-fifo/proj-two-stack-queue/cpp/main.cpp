#include <vector>
#include <stdexcept>

template <typename T>
class Queue {
    std::vector<T> in_;    // сюди пхаємо (enqueue)
    std::vector<T> out_;   // звідси знімаємо (dequeue / peek)

    void transfer() {
        // переливаємо ЛИШЕ коли вихідний порожній — інакше зламаємо порядок
        if (out_.empty()) {
            while (!in_.empty()) {
                out_.push_back(in_.back());   // друге перевертання
                in_.pop_back();
            }
        }
    }

public:
    void enqueue(const T& x) {
        in_.push_back(x);          // просто на вершину вхідного
    }

    T dequeue() {
        transfer();
        if (out_.empty()) throw std::out_of_range("черга порожня");
        T top = out_.back();
        out_.pop_back();
        return top;
    }

    const T& peek() {
        transfer();                // peek теж мусить перелити, якщо вихідний порожній
        if (out_.empty()) throw std::out_of_range("черга порожня");
        return out_.back();
    }

    std::size_t size() const {
        return in_.size() + out_.size();
    }
};
