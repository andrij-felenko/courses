    struct SweepStats { size_t expired = 0, reaped = 0, held = 0; bool panic = false; };

    SweepStats sweep(size_t budget = 4096) {
        const TimePoint now = Clock::now();
        std::vector<Entry> graveyard;      // ОГОЛОШЕНО ДО ЗАМКА: тіла руйнуються поза ним
        std::vector<Key>   reapable;
        SweepStats st;

        std::unique_lock<std::shared_mutex> g(mu_);

        // ── Фаза 1: розібрати всі події, чий час настав (не більше за бюджет).
        size_t handled = 0;
        while (!heap_.empty() && heap_.top().when <= now && handled < budget) {
            const Event ev = heap_.top();
            heap_.pop();
            ++handled;

            auto it = table_.find(ev.key);
            if (it == table_.end() || it->second.epoch != ev.epoch) continue;  // осиротілий вузлик
            Entry& e = it->second;

            if (e.deadline > now) {                       // запис оновили, поки вузлик чекав
                heap_.push(Event{e.deadline, ev.key, ev.epoch});
                continue;
            }
            if (e.live) {                                 // живий → підозрюваний
                e.live       = false;
                e.expired_at = now;
                --live_;
                ++st.expired;
                heap_.push(Event{now + grace_, ev.key, ev.epoch});
                continue;
            }
            reapable.push_back(ev.key);                   // підозрюваний, чия пільга минула
        }

        // ── Фаза 2: рішення ухвалюємо, побачивши весь тик цілком.
        panic_   = !table_.empty() &&
                   live_ * 100 < static_cast<size_t>(panic_pct_) * table_.size();
        st.panic = panic_;

        for (const Key& k : reapable) {
            auto it = table_.find(k);
            if (it == table_.end()) continue;
            const bool overdue = now - it->second.expired_at >= hard_grace_;
            if (panic_ && !overdue) {                     // не віримо масовому витіканню
                heap_.push(Event{now + grace_, k, it->second.epoch});
                ++st.held;
                continue;
            }
            graveyard.push_back(std::move(it->second));   // вантаж поїде з-під замка
            table_.erase(it);
            ++st.reaped;
        }
        return st;
    }
