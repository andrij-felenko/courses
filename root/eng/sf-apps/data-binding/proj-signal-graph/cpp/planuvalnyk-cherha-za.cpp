// ── 3. Планувальник ───────────────────────────────────────────────────
inline std::map<int, std::vector<Derived*>> buckets;

inline void enqueue(Derived& n) { buckets[n.height].push_back(&n); }

/** ФАЗА 1 — позначити застарілим усе, що нижче за течією. Жодного обчислення. */
inline void mark(Node& from) {
    std::vector<Derived*> walk(from.subs.begin(), from.subs.end());
    while (!walk.empty()) {
        Derived* n = walk.back();
        walk.pop_back();
        if (n->markedAt == epoch) continue;     // ромб не подвоює обходу
        n->markedAt = epoch;
        enqueue(*n);
        walk.insert(walk.end(), n->subs.begin(), n->subs.end());
    }
}

/** ФАЗА 2 — обчислити позначене в порядку зростання висот. */
inline void settleNode(Derived& n) {
    if (n.markedAt != epoch || n.settledAt == epoch) return;
    n.settledAt = epoch;                        // «мною вже займаються»

    bool dirty = false;
    for (Node* d : n.deps) {
        if (Derived* dd = d->asDerived()) settleNode(*dd);   // вхід має влягтися першим
        if (d->changedAt == epoch) dirty = true;
    }
    if (dirty) n.recompute();                   // ЖОДЕН вхід не змінився — не рахуємо взагалі
}

inline void settleAll() {
    while (!buckets.empty()) {
        auto it = buckets.begin();              // найменша висота
        std::vector<Derived*> bucket = std::move(it->second);
        buckets.erase(it);
        for (Derived* n : bucket) settleNode(*n);
    }
}

}  // namespace sg
