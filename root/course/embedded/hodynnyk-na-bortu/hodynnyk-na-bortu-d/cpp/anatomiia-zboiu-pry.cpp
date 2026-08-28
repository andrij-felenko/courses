// НЕПРАВИЛЬНО: використання настінного часу для таймаутів
auto deadline = std::chrono::system_clock::now() + std::chrono::seconds(5);

send_request_to_modem();

while (std::chrono::system_clock::now() < deadline) {
    if (check_modem_response()) {
        return Status::Ok;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
// Стрибок system_clock назад блокує потік на весь час зсуву
