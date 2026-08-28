while (true) {
    void* p = try_allocate(size);
    if (p) return p;

    std::new_handler handler = std::get_new_handler();
    if (!handler) {
        throw std::bad_alloc();
    }
    handler(); // Виклик користувацького обробника
}
