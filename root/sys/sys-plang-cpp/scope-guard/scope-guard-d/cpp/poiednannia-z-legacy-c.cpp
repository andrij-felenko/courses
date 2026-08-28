void resolve_and_fetch(const char* hostname) {
    addrinfo* res = nullptr;
    if (::getaddrinfo(hostname, "80", nullptr, &res) != 0) {
        throw std::runtime_error("DNS lookup failed");
    }
    // Гарантоване звільнення C-пам'яті на будь-якому шляху виходу:
    auto res_guard = ScopeGuard([res] noexcept {
        ::freeaddrinfo(res);
    });

    CURL* curl = ::curl_easy_init();
    if (!curl) throw std::runtime_error("curl init failed");
    auto curl_guard = ScopeGuard([curl] noexcept {
        ::curl_easy_cleanup(curl);
    });

    // Виконання роботи...
    // Навіть якщо обробка кине виняток, curl і res будуть звільнені деструкторами
}
