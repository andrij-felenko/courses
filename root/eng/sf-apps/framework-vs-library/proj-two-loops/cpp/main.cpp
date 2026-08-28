struct Done { long id; CURLcode code; std::string body; };

class Fetcher {
public:
    void start() { th_ = std::thread([this] { loop(); }); }

    void stop() {
        stop_.store(true, std::memory_order_relaxed);
        curl_multi_wakeup(multi_);          // єдиний спосіб урвати чужий сон ззовні
        th_.join();
    }

    std::vector<Done> drain() {             // кличе ПОТІК ВІКНА
        std::vector<Done> out;
        std::lock_guard<std::mutex> g(mx_);
        out.swap(ready_);                   // лок тримаємо наносекунди
        return out;
    }

private:
    void loop() {
        while (!stop_.load(std::memory_order_relaxed)) {
            int running = 0;
            curl_multi_perform(multi_, &running);
            reap();                                             // кладе готове в ready_ під локом
            int numfds = 0;
            curl_multi_poll(multi_, nullptr, 0, 1000, &numfds);  // ТУТ потік спить
        }
    }

    CURLM *multi_;
    std::thread th_;
    std::atomic<bool> stop_{false};
    std::mutex mx_;
    std::vector<Done> ready_;
};
