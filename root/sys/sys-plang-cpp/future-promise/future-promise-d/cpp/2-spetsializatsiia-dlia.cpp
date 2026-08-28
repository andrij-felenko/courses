struct HeavyStruct { /* ... */ };

HeavyStruct global_data;

std::promise<HeavyStruct&> p;
std::future<HeavyStruct&> f = p.get_future();

std::thread t([&p]() {
    p.set_value(global_data); // Передаємо посилання
});

HeavyStruct& ref = f.get(); // Отримуємо посилання на global_data
t.join();
