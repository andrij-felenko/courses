int main() {
    auto work = std::execution::schedule(pool.get_scheduler())
              | std::execution::then([] { return 42; });

    auto result = std::execution::sync_wait(std::move(work));

    if (result.has_value()) {
        auto [val] = *result;
        std::cout << "Отримано значення: " << val << std::endl;
    }
}
