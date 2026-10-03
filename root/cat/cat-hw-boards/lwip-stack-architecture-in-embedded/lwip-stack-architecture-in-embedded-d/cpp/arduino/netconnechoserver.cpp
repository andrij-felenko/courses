#include <lwip/api.h>
#include <lwip/sockets.h>

class NetconnEchoServer {
private:
    uint16_t _port;
public:
    explicit NetconnEchoServer(uint16_t port) : _port(port) {}

    void run() {
        netconn* listener = netconn_new(NETCONN_TCP);
        if (!listener) return;

        netconn_bind(listener, IP_ADDR_ANY, _port);
        netconn_listen(listener);

        netconn* client = nullptr;
        while (netconn_accept(listener, &client) == ERR_OK) {
            netbuf* buf = nullptr;
            while (netconn_recv(client, &buf) == ERR_OK) {
                void* data = nullptr;
                u16_t len = 0;
                netbuf_data(buf, &data, &len);
                netconn_write(client, data, len, NETCONN_COPY);
                netbuf_delete(buf);
            }
            netconn_close(client);
            netconn_delete(client);
        }
    }
};

class BsdSocketEchoServer {
private:
    uint16_t _port;
public:
    explicit BsdSocketEchoServer(uint16_t port) : _port(port) {}

    void run() {
        int fd = lwip_socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return;

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(_port);
        addr.sin_addr.s_addr = IPADDR_ANY;

        lwip_bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
        lwip_listen(fd, 2);

        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        int client_fd = lwip_accept(fd, reinterpret_cast<sockaddr*>(&client_addr), &client_len);

        if (client_fd >= 0) {
            char buffer[64];
            int bytes_read = lwip_recv(client_fd, buffer, sizeof(buffer), 0);
            if (bytes_read > 0) {
                lwip_send(client_fd, buffer, bytes_read, 0);
            }
            lwip_close(client_fd);
        }
        lwip_close(fd);
    }
};
