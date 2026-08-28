#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    typedef SOCKET socket_t;
    #define CLOSE_SOCKET(s) closesocket(s)
#else
    #include <unistd.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/tcp.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <sys/time.h>
    typedef int socket_t;
    #define INVALID_SOCKET (-1)
    #define SOCKET_ERROR   (-1)
    #define CLOSE_SOCKET(s) close(s)
#endif

typedef struct {
    socket_t sock;
    char     ip_address[64];
    uint16_t port;
    uint32_t timeout_ms;
} scpi_client_t;

typedef enum {
    SCPI_SUCCESS = 0,
    SCPI_ERR_CONNECT = -1,
    SCPI_ERR_SEND = -2,
    SCPI_ERR_TIMEOUT = -3,
    SCPI_ERR_RESPONSE = -4,
    SCPI_ERR_INSTRUMENT = -5
} scpi_status_t;

static bool init_network_subsystem(void) {
#ifdef _WIN32
    WSADATA wsa;
    return (WSAStartup(MAKEWORD(2, 2), &wsa) == 0);
#else
    return true;
#endif
}

static void cleanup_network_subsystem(void) {
#ifdef _WIN32
    WSACleanup();
#endif
}

scpi_status_t scpi_connect(scpi_client_t *client, const char *ip, uint16_t port, uint32_t timeout_ms) {
    if (!client || !ip) return SCPI_ERR_CONNECT;
    
    strncpy(client->ip_address, ip, sizeof(client->ip_address) - 1);
    client->port = port;
    client->timeout_ms = timeout_ms;
    client->sock = INVALID_SOCKET;

    client->sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (client->sock == INVALID_SOCKET) {
        return SCPI_ERR_CONNECT;
    }

    // Вимкнення алгоритму Нейгла для усунення затримок 200 мс
    int flag = 1;
    setsockopt(client->sock, IPPROTO_TCP, TCP_NODELAY, (char *)&flag, sizeof(int));

#ifdef _WIN32
    DWORD tv = timeout_ms;
    setsockopt(client->sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));
    setsockopt(client->sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(tv));
#else
    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    setsockopt(client->sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(client->sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));
#endif

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, ip, &serv_addr.sin_addr) <= 0) {
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
        return SCPI_ERR_CONNECT;
    }

    if (connect(client->sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
        return SCPI_ERR_CONNECT;
    }

    return SCPI_SUCCESS;
}

void scpi_disconnect(scpi_client_t *client) {
    if (client && client->sock != INVALID_SOCKET) {
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
    }
}

scpi_status_t scpi_send_command(scpi_client_t *client, const char *cmd) {
    if (!client || client->sock == INVALID_SOCKET || !cmd) return SCPI_ERR_SEND;

    size_t cmd_len = strlen(cmd);
    char buffer[1024];
    
    if (cmd_len + 2 >= sizeof(buffer)) return SCPI_ERR_SEND;
    memcpy(buffer, cmd, cmd_len);
    
    if (buffer[cmd_len - 1] != '\n') {
        buffer[cmd_len] = '\n';
        cmd_len++;
    }

    size_t total_sent = 0;
    while (total_sent < cmd_len) {
        int sent = send(client->sock, buffer + total_sent, (int)(cmd_len - total_sent), 0);
        if (sent <= 0) {
            return SCPI_ERR_SEND;
        }
        total_sent += (size_t)sent;
    }

    return SCPI_SUCCESS;
}

scpi_status_t scpi_read_response(scpi_client_t *client, char *out_buf, size_t max_len) {
    if (!client || client->sock == INVALID_SOCKET || !out_buf || max_len == 0) {
        return SCPI_ERR_RESPONSE;
    }

    size_t total_read = 0;
    while (total_read < max_len - 1) {
        char ch;
        int received = recv(client->sock, &ch, 1, 0);
        if (received <= 0) {
            if (total_read > 0) break;
            return SCPI_ERR_TIMEOUT;
        }
        if (ch == '\r') continue;
        if (ch == '\n') break;
        
        out_buf[total_read++] = ch;
    }

    out_buf[total_read] = '\0';
    return SCPI_SUCCESS;
}

scpi_status_t scpi_query(scpi_client_t *client, const char *query, char *out_buf, size_t max_len) {
    scpi_status_t status = scpi_send_command(client, query);
    if (status != SCPI_SUCCESS) return status;
    return scpi_read_response(client, out_buf, max_len);
}

scpi_status_t scpi_check_errors(scpi_client_t *client) {
    char resp[256];
    while (1) {
        scpi_status_t st = scpi_query(client, ":SYSTem:ERRor?", resp, sizeof(resp));
        if (st != SCPI_SUCCESS) return st;

        int error_code = 0;
        char error_msg[200] = {0};
        if (sscanf(resp, "%d,\"%199[^\"]\"", &error_code, error_msg) < 1) {
            sscanf(resp, "%d", &error_code);
        }

        if (error_code == 0) {
            break;
        }

        fprintf(stderr, "[SCPI ERROR %s:%u] Код %d: %s\n", 
                client->ip_address, client->port, error_code, error_msg);
        return SCPI_ERR_INSTRUMENT;
    }
    return SCPI_SUCCESS;
}

int main(void) {
    init_network_subsystem();

    scpi_client_t dmm;
    printf("Підключення до мультиметра 192.168.1.105:5025...\n");
    if (scpi_connect(&dmm, "192.168.1.105", 5025, 2000) != SCPI_SUCCESS) {
        fprintf(stderr, "Помилка підключення до приладу!\n");
        cleanup_network_subsystem();
        return EXIT_FAILURE;
    }

    char idn[256];
    if (scpi_query(&dmm, "*IDN?", idn, sizeof(idn)) == SCPI_SUCCESS) {
        printf("Ідентифікатор: %s\n", idn);
    }

    scpi_send_command(&dmm, "*RST");
    scpi_send_command(&dmm, "*CLS");
    scpi_send_command(&dmm, ":SENSe:VOLTage:DC:RANGe 10.0");
    scpi_send_command(&dmm, ":SENSe:VOLTage:DC:NPLC 10");

    if (scpi_check_errors(&dmm) == SCPI_SUCCESS) {
        char val_str[64];
        if (scpi_query(&dmm, ":MEASure:VOLTage:DC?", val_str, sizeof(val_str)) == SCPI_SUCCESS) {
            double voltage = strtod(val_str, NULL);
            printf("Виміряна напруга: %.7f В\n", voltage);
        }
    }

    scpi_disconnect(&dmm);
    cleanup_network_subsystem();
    return EXIT_SUCCESS;
}
