// Інтеграція з асинхронною мережевою корутиною Boost.Asio / C++20
awaitable<std::expected<std::string, SocketError>> async_read_packet(tcp::socket& socket) {
    char buffer[1024];
    sys::error_code ec;
    size_t n = co_await socket.async_read_some(asio::buffer(buffer), redirect_error(use_awaitable, ec));
    
    if (ec) {
        co_return std::unexpected(SocketError::ReadTimeout);
    }
    co_return std::string(buffer, n);
}
