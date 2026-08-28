std::packaged_task<double(double, double)> task([](double a, double b) {
    if (b == 0.0) throw std::invalid_argument("Ділення на нуль!");
    return a / b;
});

std::future<double> fut = task.get_future();
std::thread worker(std::move(task), 10.0, 0.0);
worker.detach();

try {
    double res = fut.get(); // Повторно кидає std::invalid_argument
} catch (const std::exception& e) {
    std::cout << "Перехоплено виняток з фонового потоку: " << e.what() << std::endl;
}
