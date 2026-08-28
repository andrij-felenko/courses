#include <atomic>
#include <iostream>
#include <thread>

std::string make_text(int seed) {
    std::string s;
    for (int i = 0; i < 400; ++i) {            // рівно 400 слів
        s += "word";
        s += char('a' + (seed + i) % 26);
        s += ' ';
    }
    return s;
}

int main() {
    std::size_t bad = 0;

    for (int round = 0; round < 50000; ++round) {
        Document doc(make_text(round));        // свіжий об'єкт: кеш порожній
        std::atomic<int> gate{0};
        std::size_t a = 0, b = 0;

        auto worker = [&](std::size_t& out) {
            gate.fetch_add(1, std::memory_order_relaxed);
            while (gate.load(std::memory_order_relaxed) < 2)   // стартуємо разом
                std::this_thread::yield();
            out = doc.word_count();
        };

        std::thread t1(worker, std::ref(a));
        std::thread t2(worker, std::ref(b));
        t1.join();
        t2.join();

        if (a != 400 || b != 400) ++bad;
    }
    std::cout << "неправильних відповідей: " << bad << " із 100000\n";
}
