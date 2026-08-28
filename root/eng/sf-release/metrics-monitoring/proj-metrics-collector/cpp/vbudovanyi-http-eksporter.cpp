#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <thread>

void start_metrics_server(const telemetry::Registry& registry, uint16_t port) {
    std::thread([&registry, port]() {
        int server_fd = socket(AF_INET, SOCK_STREAM, 0);
        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        bind(server_fd, (sockaddr*)&addr, sizeof(addr));
        listen(server_fd, 16);

        while (true) {
            int client_fd = accept(server_fd, nullptr, nullptr);
            if (client_fd < 0) continue;

            // Зчитування HTTP-запиту GET /metrics
            char req_buf[512];
            ssize_t n = read(client_fd, req_buf, sizeof(req_buf) - 1);
            if (n > 0) {
                std::string body = registry.render_openmetrics();
                std::string header = std::format(
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/openmetrics-text; version=1.0.0; charset=utf-8\r\n"
                    "Content-Length: {}\r\n"
                    "Connection: close\r\n\r\n",
                    body.size()
                );

                write(client_fd, header.data(), header.size());
                write(client_fd, body.data(), body.size());
            }
            close(client_fd);
        }
    }).detach();
}
