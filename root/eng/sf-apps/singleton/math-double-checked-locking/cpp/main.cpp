#include <atomic>
#include <mutex>

class Foo {
    static std::atomic<Helper*> instance;
    static std::mutex m;
public:
    static Helper* getHelper() {
        Helper* p = instance.load(std::memory_order_acquire);   // acquire
        if (p == nullptr) {
            std::lock_guard<std::mutex> lock(m);
            p = instance.load(std::memory_order_relaxed);       // під замком relaxed досить
            if (p == nullptr) {
                p = new Helper();                                // конструктор до кінця…
                instance.store(p, std::memory_order_release);    // …ПОТІМ публікація (release)
            }
        }
        return p;
    }
};
