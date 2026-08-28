auto fut = std::async(std::launch::async, heavy_job);

// Періодичне опитування стану з тайм-аутом у 50 мілісекунд
while (fut.wait_for(std::chrono::milliseconds(50)) == std::future_status::timeout) {
    // Головний потік може малювати UI або обробляти події
    render_loading_spinner();
}

// Результат гарантовано готовий!
auto result = fut.get();
