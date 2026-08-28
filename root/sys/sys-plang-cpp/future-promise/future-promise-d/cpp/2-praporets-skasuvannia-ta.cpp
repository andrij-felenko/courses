void cancellable_worker(std::stop_token stop_tok, std::promise<int> p) {
    for (int i = 0; i < 100; ++i) {
        if (stop_tok.stop_requested()) {
            p.set_exception(std::make_exception_ptr(
                std::runtime_error("Операцію скасовано користувачем!")
            ));
            return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    p.set_value(42);
}
