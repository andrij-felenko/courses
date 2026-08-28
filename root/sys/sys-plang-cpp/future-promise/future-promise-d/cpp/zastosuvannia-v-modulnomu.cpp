void test_async_service_failure() {
    std::promise<std::string> mock_promise;
    std::future<std::string> mock_future = mock_promise.get_future();

    // Передаємо mock_future у тестувальну систему
    ServiceConsumer service(std::move(mock_future));

    // Штучно симулюємо відмову мережі
    mock_promise.set_exception(std::make_exception_ptr(
        std::runtime_error("Timeout connection failure")
    ));

    // Перевіряємо реакцію сервісу на виняток
    assert(service.has_error_state());
}
