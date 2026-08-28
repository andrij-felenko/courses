using namespace std::chrono_literals;

std::future<int> f = launch_async_computation();

// Очікуємо максимум 200 мілісекунд
std::future_status status = f.wait_for(200ms);

switch (status) {
    case std::future_status::ready:
        std::cout << "Результат готовий: " << f.get() << std::endl;
        break;
    case std::future_status::timeout:
        std::cout << "Час вичерпано, фоновий потік ще працює..." << std::endl;
        break;
    case std::future_status::deferred:
        std::cout << "Задача відкладена (lazy evaluation)" << std::endl;
        break;
}
