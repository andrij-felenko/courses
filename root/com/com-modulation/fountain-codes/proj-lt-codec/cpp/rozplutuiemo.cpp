#include <algorithm>
#include <memory>

struct Drop { std::vector<int> idx; Bytes val; };   // невідомі індекси + XOR-вантаж

struct LTDecoder {
    int k;
    std::vector<double> mu;
    std::vector<Bytes> blocks;                       // відновлені блоки
    std::vector<bool> known;
    int recovered = 0;
    std::vector<std::vector<Drop*>> contains;        // блок → краплі, що його містять
    std::vector<std::unique_ptr<Drop>> pool;         // володіння краплями

    LTDecoder(int k_, std::vector<double> m)
        : k(k_), mu(std::move(m)), blocks(k_), known(k_, false), contains(k_) {}

    void add(uint64_t seed, const Bytes& payload) {
        Bytes val = payload;
        std::vector<int> unknown;
        for (int i : droplet_recipe(seed, k, mu)) {
            if (known[i]) xor_into(val, blocks[i]);   // одразу вирізаємо вже відоме
            else unknown.push_back(i);
        }
        if (unknown.empty()) return;                  // надлишкова крапля
        pool.push_back(std::make_unique<Drop>(Drop{unknown, std::move(val)}));
        Drop* d = pool.back().get();
        for (int i : unknown) contains[i].push_back(d);
        if (unknown.size() == 1) peel(d);
    }

    void peel(Drop* start) {
        std::vector<Drop*> ripple{start};             // черга крапель степеня 1
        while (!ripple.empty()) {
            Drop* d = ripple.back();
            ripple.pop_back();
            if (d->idx.size() != 1) continue;         // степінь міг змінитись у черзі
            int i = d->idx[0];
            if (known[i]) continue;
            blocks[i] = d->val;                        // відкрили блок i
            known[i] = true;
            ++recovered;
            for (Drop* nb : contains[i]) {             // виріж i з усіх його сусідів
                auto it = std::find(nb->idx.begin(), nb->idx.end(), i);
                if (it == nb->idx.end()) continue;
                xor_into(nb->val, blocks[i]);
                nb->idx.erase(it);
                if (nb->idx.size() == 1) ripple.push_back(nb);
            }
            contains[i].clear();
        }
    }

    bool done() const { return recovered == k; }
};
