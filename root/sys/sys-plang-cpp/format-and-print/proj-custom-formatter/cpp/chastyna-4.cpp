int main() {
    // 1. Тестування форматування матриці
    Matrix3x3 mat{1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0};

    std::cout << "--- Друк Matrix3x3 ---\n";
    std::cout << "Багаторядковий:\n" << std::format("{:.2f}", mat) << "\n\n";
    std::cout << "Однорядковий: " << std::format("{:1.1f}", mat) << "\n\n";

    // 2. Тестування форматування логу
    LogRecord rec{
        .timestamp = std::chrono::system_clock::now(),
        .level = LogLevel::Info,
        .component = "HTTP/Server",
        .message = "GET /api/v1/status HTTP/1.1 200 OK"
    };

    std::cout << "--- Друк LogRecord ---\n";
    std::cout << std::format("Full: {}", rec) << "\n";
    std::cout << std::format("JSON: {:j}", rec) << "\n";
    std::cout << std::format("Short: {:s}", rec) << "\n\n";

    // 3. Високпродуктивне безалокаційне логування
    std::cout << "--- FastLogger ---\n";
    FastLogger<256>::log("Record: {:j}", rec);
    FastLogger<256>::log("Matrix state: {:1.2f}", mat);

    return 0;
}
