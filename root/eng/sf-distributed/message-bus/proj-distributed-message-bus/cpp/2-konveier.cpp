enum class InterceptorResult {
    Continue,
    Drop,
    Error
};

using Interceptor = std::function<InterceptorResult(MessageEnvelope&)>;

/* 1. Фабрика перехоплювача валідації схеми */
Interceptor make_schema_validator(uint32_t min_version) {
    return [min_version](MessageEnvelope& env) {
        if (env.schema_version < min_version) {
            std::cout << std::format("[Interceptor:Schema] ВІДХИЛЕНО: версія v{} застаріла (потрібна >= v{})\n",
                                     env.schema_version, min_version);
            return InterceptorResult::Drop;
        }
        std::cout << std::format("[Interceptor:Schema] OK: версія v{} сумісна\n", env.schema_version);
        return InterceptorResult::Continue;
    };
}

/* 2. Перехоплювач трасування та логування */
Interceptor make_tracing_logger() {
    return [](MessageEnvelope& env) {
        std::cout << std::format("[Interceptor:Tracing] Обробка [{}] Тема='{}' Trace='{}' Corr='{}'\n",
                                 env.message_id, env.topic, env.traceparent, env.correlation_id);
        return InterceptorResult::Continue;
    };
}

/* 3. Перехоплювач дедуплікації */
class DedupInterceptor {
    std::unordered_set<std::string> seen_ids_;
public:
    InterceptorResult operator()(MessageEnvelope& env) {
        if (seen_ids_.contains(env.message_id)) {
            std::cout << std::format("[Interceptor:Dedup] ВІДХИЛЕНО: дублікат повідомлення {}\n", env.message_id);
            return InterceptorResult::Drop;
        }
        seen_ids_.insert(env.message_id);
        return InterceptorResult::Continue;
    }
};
