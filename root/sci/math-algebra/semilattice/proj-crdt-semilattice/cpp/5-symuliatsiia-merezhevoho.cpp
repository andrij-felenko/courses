#include <vector>
#include <algorithm>
#include <random>

struct NetworkMessage {
    size_t from_node;
    size_t to_node;
    PNCounter payload;
};

int main() {
    std::vector<PNCounter> cluster = {
        PNCounter("node-0"),
        PNCounter("node-1"),
        PNCounter("node-2")
    };

    // Виконуємо локальні операції на вузлах
    cluster[0].increment(15);
    cluster[0].decrement(3);  // Net: +12

    cluster[1].increment(8);
    cluster[1].decrement(2);  // Net: +6

    cluster[2].increment(30);
    cluster[2].decrement(10); // Net: +20

    // Формуємо чергу повідомлень для повного взаємного обміну
    std::vector<NetworkMessage> network_queue;
    for (size_t i = 0; i < cluster.size(); ++i) {
        for (size_t j = 0; j < cluster.size(); ++j) {
            if (i != j) {
                // Додаємо оригінальне повідомлення
                network_queue.push_back({i, j, cluster[i]});
                // Штучно дублюємо кожне друге повідомлення для тесту ідемпотентності
                if ((i + j) % 2 == 0) {
                    network_queue.push_back({i, j, cluster[i]});
                }
            }
        }
    }

    // Перемішуємо повідомлення для імітації хаотичних мережевих затримок
    std::mt19937 rng(42);
    std::shuffle(network_queue.begin(), network_queue.end(), rng);

    // Доставляємо пакети з черги адресатам
    for (const auto& msg : network_queue) {
        cluster[msg.to_node].merge(msg.payload);
    }

    // Перевірка збіжності: 12 + 6 + 20 = 38 на кожному вузлі
    bool all_converged = true;
    const int64_t expected_value = 38;

    for (size_t i = 0; i < cluster.size(); ++i) {
        std::cout << "Вузол " << i << " стан: " << cluster[i].value() << "\n";
        if (cluster[i].value() != expected_value) {
            all_converged = false;
        }
    }

    if (all_converged) {
        std::cout << "Успіх: усі репліки детерміновано зійшлися до значення 38 завдяки напіврешітці.\n";
    }

    return 0;
}
