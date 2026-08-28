void Store::trim() {
    // Курсор на дні (людина відкотилася в самий початок) — з дна брати нема чого:
    // там лежить теперішній стан. Тоді бюджет доводиться відбирати з іншого кінця,
    // зрізаючи найдальші кроки повтору, — і «вперед» перестане діставати до кінця.
    while (bytes_ > budget_ && steps_.size() > 1 && index_ > 0) {
        bytes_ -= steps_.front().weight;
        Step dead = std::move(steps_.front());
        steps_.pop_front();
        --index_;                                     // курсор з'їхав разом із дном
        if (saved_ >= 0) saved_ = (saved_ > 0 ? saved_ - 1 : -1);
        retire(std::move(dead));                      // ← тут «вилучене» нарешті помирає
    }
}

// Фоновий прибиральник. Крок, що випав із історії, — останній власник усього, що бачив
// лише він; його деструктор може звільняти сотні тисяч вузлів, а це помітна пауза.
// Вузли незмінні, лічильники shared_ptr атомарні — тож помирати в чужому потоці їм безпечно.
class Disposer {
public:
    Disposer() : th_([this] { loop(); }) {}
    ~Disposer() {
        { std::lock_guard lk(m_); stop_ = true; }
        cv_.notify_all();
        th_.join();
    }
    void post(Step dead) {
        { std::lock_guard lk(m_); q_.push_back(std::move(dead)); }
        cv_.notify_one();
    }
private:
    void loop() {
        for (;;) {
            std::deque<Step> batch;
            {
                std::unique_lock lk(m_);
                cv_.wait(lk, [this] { return stop_ || !q_.empty(); });
                if (stop_ && q_.empty()) return;
                batch.swap(q_);
            }
            batch.clear();     // ← ось тут і звільняються вузли, які тримала історія
        }
    }
    std::deque<Step>        q_;
    std::mutex              m_;
    std::condition_variable cv_;
    bool                    stop_ = false;
    std::thread             th_;
};

void Store::retire(Step dead) { disposer_.post(std::move(dead)); }
