class Worker {
public:
    Worker() {
        // Фоновий потік стартує ДО завершення конструктора похідного класу!
        m_thread = std::thread([this]() {
            this->do_work(); // ГОНКА: vptr може ще вказувати на vtable for Worker!
        });
    }

    virtual ~Worker() {
        if (m_thread.joinable()) m_thread.join();
    }

    virtual void do_work() = 0;

private:
    std::thread m_thread;
};
