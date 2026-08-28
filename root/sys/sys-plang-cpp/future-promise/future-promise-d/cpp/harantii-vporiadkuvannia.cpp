int shared_payload = 0; // Неатомарна змінна без м'ютекса!

std::promise<void> p;
std::future<void> f = p.get_future();

std::thread producer([&]() {
    shared_payload = 42; // Модифікація звичайного поля
    p.set_value();       // Релізний бар'єр пам'яті
});

std::thread consumer([&]() {
    f.wait();            // Аквізиційний бар'єр пам'яті
    // Гарантовано прочитає 42 без data race!
    std::cout << shared_payload << std::endl; 
});
