std::future<int> f;
{
    std::promise<int> p;
    f = p.get_future();
} // Об'єкт p знищується тут без set_value!

try {
    int val = f.get(); // Кине std::future_error
} catch (const std::future_error& e) {
    if (e.code() == std::future_errc::broken_promise) {
        std::cout << "Обіцянка порушена: виробник загинув без результату!" << std::endl;
    }
}
