class MessageBus {
public:
    using Handler = std::function<void(const MessageEnvelope&)>;

    void add_interceptor(Interceptor interceptor) {
        interceptors_.push_back(std::move(interceptor));
    }

    void subscribe(std::string_view topic_pattern, Handler handler) {
        subscriptions_.emplace_back(std::string(topic_pattern), std::move(handler));
    }

    bool publish(MessageEnvelope& env) {
        /* 1. Конвеєр перехоплювачів */
        for (auto& interceptor : interceptors_) {
            if (interceptor(env) != InterceptorResult::Continue) {
                return false;
            }
        }

        /* 2. Маршрутизація */
        size_t delivered = 0;
        for (const auto& [pattern, handler] : subscriptions_) {
            if (matches(pattern, env.topic)) {
                handler(env);
                ++delivered;
            }
        }
        std::cout << std::format("[Bus:Router] Повідомлення '{}' успішно доставлено {} підписникам\n", 
                                 env.topic, delivered);
        return true;
    }

private:
    static bool matches(std::string_view pattern, std::string_view topic) {
        if (pattern.ends_with(".*")) {
            auto prefix = pattern.substr(0, pattern.size() - 2);
            return topic.starts_with(prefix);
        }
        return pattern == topic;
    }

    std::vector<Interceptor> interceptors_;
    std::vector<std::pair<std::string, Handler>> subscriptions_;
};
