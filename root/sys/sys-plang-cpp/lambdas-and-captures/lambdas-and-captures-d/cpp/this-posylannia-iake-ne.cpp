class Session : public std::enable_shared_from_this<Session> {
public:
    void start(Timer& timer) {
        std::weak_ptr<Session> weak = weak_from_this();
        timer.every(std::chrono::seconds(1), [weak] {
            if (auto self = weak.lock()) self->tick();   // об'єкт живий — працюємо
        });                                              // помер — тихо нічого не робимо
    }
private:
    void tick();
};
