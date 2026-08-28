struct EndpointConfig {
    // 1. Мережевий транспорт та брокер
    std::string broker_endpoint_url;
    std::string queue_or_topic_name;
    std::string consumer_group_id;
    
    // 2. Якість обслуговування (QoS) та префетч
    uint16_t prefetch_count = 50;           // Максимум непідтверджених повідомлень
    bool enable_auto_ack = false;           // Суворо заборонено для надійних систем
    
    // 3. Пул воркерів та шардування
    uint16_t worker_threads_count = 8;      // Кількість паралельних ниток обробки
    size_t worker_queue_capacity = 1000;    // Максимальна глибина черги одного воркера
    
    // 4. Пороги протитиску (Backpressure Watermarks)
    double high_watermark_ratio = 0.80;     // При 80% заповнення буферів -> pause()
    double low_watermark_ratio = 0.20;      // При спаді заповнення до 20% -> resume()
    
    // 5. Політика повторів (Retry Policy)
    uint32_t max_retry_attempts = 5;
    std::chrono::milliseconds initial_retry_interval{100};
    std::chrono::milliseconds max_retry_interval{30000};
    double backoff_multiplier = 2.0;
    bool enable_full_jitter = true;
    
    // 6. Мертва черга (DLQ)
    std::string dlq_topic_name = "dead_letter_queue";
    
    // 7. Безпечне завершення (Graceful Shutdown)
    std::chrono::milliseconds drain_timeout{25000};
};
