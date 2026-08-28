using SlotByValue = void (*)(Vehicle *, const void *, Message);
using SlotByRef   = void (*)(Vehicle *, const void *, const Message &);

// Різниця між цими двома функціями — один символ «&» у параметрі.
void slotByValue(Vehicle *v, const void *l, Message m)         { v->onMessage(l, m); }
void slotByRef  (Vehicle *v, const void *l, const Message &m)  { v->onMessage(l, m); }

// ── Схема 1: віддати всім, хай кожен фільтрує сам ────────────────────────
struct FanoutBus {
    std::vector<std::pair<Vehicle *, SlotByValue>> byValue;
    std::vector<std::pair<Vehicle *, SlotByRef>>   byRef;

    void subscribe(Vehicle *v) {
        byValue.emplace_back(v, &slotByValue);
        byRef.emplace_back(v, &slotByRef);
    }
    void deliverByValue(const void *l, const Message &m) {
        for (const auto &c : byValue) { c.second(c.first, l, m); }   // копія кожному
    }
    void deliverByRef(const void *l, const Message &m) {
        for (const auto &c : byRef) { c.second(c.first, l, m); }     // копій нема
    }
};

// ── Схема 2: таблиця «номер системи → об'єкт» ─────────────────────────────
struct TableBus {
    std::array<Vehicle *, 256> bySysid{};    // 256 · 8 Б = 2 КБ, лізе в перший рівень кешу
    std::vector<Vehicle *>     all;          // для того, що адресоване не одному

    void add(Vehicle *v) { bySysid[v->sysid] = v; all.push_back(v); }

    void remove(Vehicle *v) {
        if (bySysid[v->sysid] == v) { bySysid[v->sysid] = nullptr; }
        for (size_t i = 0; i < all.size(); ++i) {
            if (all[i] == v) { all.erase(all.begin() + i); break; }
        }
    }

    void deliver(const void *l, const Message &m) {
        if (m.sysid == 0) {                              // джерело не назвало себе
            for (Vehicle *v : all) { v->onMessage(l, m); }
            return;
        }
        if (m.msgid == MSG_RADIO_STATUS) {               // доповідь модема про канал
            for (Vehicle *v : all) {
                if (v->usesLink(l)) { v->onMessage(l, m); }
            }
            return;
        }
        if (Vehicle *v = bySysid[m.sysid]) { v->onMessage(l, m); }
    }
};
