struct TelemetryLogger {
    void log_status(int code, double latency) {
        std::cout << "[Telemetry] Код: " << code << ", Затримка: " << latency << " мс\n";
    }
};

void test_event_observer() {
    TelemetryLogger logger;
    // CTAD автоматично виводить: Receiver = TelemetryLogger, ReturnType = void, Args = {int, double}
    EventObserver observer(&TelemetryLogger::log_status, &logger);

    observer.trigger(200, 1.45);
}
