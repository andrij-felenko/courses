void run_telemetry_service() {
    // Створюємо планувальники для мережевого вводу/виводу та математичного пулу
    std::execution::run_loop io_loop;
    std::execution::run_loop compute_pool;

    auto io_sched = io_loop.get_scheduler();
    auto compute_sched = compute_pool.get_scheduler();

    RawTelemetryPacket packet{
        .packet_id = 10842,
        .raw_altitude = 4520.0,
        .raw_velocity = 64.2,
        .gyro_x = 0.45,
        .gyro_y = 0.12,
        .gyro_z = 0.33,
        .checksum_valid = true
    };

    // 1. Створення графа задач (Sender)
    auto pipeline_sender = make_telemetry_pipeline(packet, io_sched, compute_sched);

    // 2. Матеріалізація стану та синхронне очікування результату
    std::optional<std::tuple<bool>> execution_result = std::this_thread::sync_wait(std::move(pipeline_sender));

    if (execution_result.has_value() && std::get<0>(*execution_result)) {
        std::cout << "[SYSTEM] Телеметрію успішно збережено в базі даних." << std::endl;
    }
}
