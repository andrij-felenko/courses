void process_resource(std::unique_ptr<int> data) {
    std::cout << "Processing value: " << *data << "\n";
}

void move_resource_to_thread() {
    auto ptr = std::make_unique<int>(42);
    // Передаємо володіння об'єктом у новий потік через std::move
    std::thread t(process_resource, std::move(ptr));
    t.join();
    // ptr тепер дорівнює nullptr
}
