void update_data(int& value) {
    value = 100;
}

void incorrect_thread_argument() {
    int x = 10;
    // ПОМИЛКА КОМПІЛЯЦІЇ! std::thread копіює x у rvalue, яке не може прив'язатися до int&
    // std::thread t(update_data, x); 

    // ПРАВИЛЬНО: Використання std::ref створює std::reference_wrapper<int>
    std::thread t(update_data, std::ref(x));
    t.join();
    // x тепер дорівнює 100
}
