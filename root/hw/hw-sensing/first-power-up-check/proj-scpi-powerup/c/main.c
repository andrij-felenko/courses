#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  typedef SOCKET socket_t;
  #define CLOSE_SOCKET closesocket
  #define SLEEP_MS(ms) Sleep(ms)
#else
  #include <unistd.h>
  #include <sys/types.h>
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  typedef int socket_t;
  #define INVALID_SOCKET (-1)
  #define SOCKET_ERROR (-1)
  #define CLOSE_SOCKET close
  #define SLEEP_MS(ms) usleep((ms) * 1000)
#endif

typedef struct {
    socket_t sock;
    char ip[64];
    int port;
} ScpiClient;

bool scpi_connect(ScpiClient *client, const char *ip, int port) {
    strncpy(client->ip, ip, sizeof(client->ip) - 1);
    client->port = port;

#if defined(_WIN32)
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        fprintf(stderr, "Помилка ініціалізації Winsock WSAStartup\n");
        return false;
    }
#endif

    client->sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (client->sock == INVALID_SOCKET) {
        fprintf(stderr, "Не вдалося створити мережевий TCP сокет\n");
        return false;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons((unsigned short)port);
    inet_pton(AF_INET, ip, &server_addr.sin_addr);

    if (connect(client->sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        fprintf(stderr, "Помилка з'єднання з блоком живлення за адресою %s:%d\n", ip, port);
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
        return false;
    }

    return true;
}

void scpi_disconnect(ScpiClient *client) {
    if (client->sock != INVALID_SOCKET) {
        // Обов'язкове захисне вимкнення силового виходу перед розривом сесії
        send(client->sock, "OUTP OFF\n", 9, 0);
        CLOSE_SOCKET(client->sock);
        client->sock = INVALID_SOCKET;
    }
#if defined(_WIN32)
    WSACleanup();
#endif
}

bool scpi_send(ScpiClient *client, const char *cmd) {
    if (client->sock == INVALID_SOCKET) return false;
    int len = (int)strlen(cmd);
    int sent = send(client->sock, cmd, len, 0);
    return sent == len;
}

bool scpi_query(ScpiClient *client, const char *cmd, char *buf, size_t buf_size) {
    if (!scpi_send(client, cmd)) return false;
    int received = recv(client->sock, buf, (int)(buf_size - 1), 0);
    if (received <= 0) return false;
    buf[received] = '\0';
    // Видаляємо кінцеві символи нового рядка
    char *nl = strchr(buf, '\n');
    if (nl) *nl = '\0';
    char *cr = strchr(buf, '\r');
    if (cr) *cr = '\0';
    return true;
}

double scpi_measure_current(ScpiClient *client) {
    char response[64];
    if (scpi_query(client, "MEAS:CURR?\n", response, sizeof(response))) {
        return atof(response);
    }
    return -1.0;
}

bool run_safe_bringup(ScpiClient *client, double target_voltage, double current_limit, double max_safe_quiescent) {
    char cmd[128];
    char idn[128];

    // Ідентифікація приладу
    if (scpi_query(client, "*IDN?\n", idn, sizeof(idn))) {
        printf("Підключено до вимірювального приладу: %s\n", idn);
    }

    // Скидання приладу та попереднє налаштування обмеження струму
    scpi_send(client, "*RST\n");
    SLEEP_MS(200);

    snprintf(cmd, sizeof(cmd), "CURR %.4f\n", current_limit);
    scpi_send(client, cmd);
    scpi_send(client, "VOLT 0.0\n");
    scpi_send(client, "OUTP ON\n");
    SLEEP_MS(100);

    printf("Початок плавного наростання напруги (Апаратний ліміт: %.1f мА, Ціль: %.2f В)...\n",
           current_limit * 1000.0, target_voltage);

    double v_step = 0.20;
    for (double v = 0.20; v <= target_voltage + 0.001; v += v_step) {
        snprintf(cmd, sizeof(cmd), "VOLT %.3f\n", v);
        scpi_send(client, cmd);
        SLEEP_MS(100);

        double i_meas = scpi_measure_current(client);
        if (i_meas < 0.0) {
            fprintf(stderr, "Помилка зчитування струму з шини SCPI!\n");
            scpi_send(client, "OUTP OFF\n");
            return false;
        }

        printf("  Напруга: %5.2f В | Виміряний струм: %6.2f мА\n", v, i_meas * 1000.0);

        // Перевірка перевищення струму спокою холостого ходу
        if (i_meas > max_safe_quiescent) {
            fprintf(stderr, "\n[УВАГА] Перевищення безпечного струму спокою! Зафіксовано %.2f мА при %.2f В\n",
                    i_meas * 1000.0, v);
            fprintf(stderr, "[АВАРІЯ] Негайне знеструмлення виходу (OUTP OFF).\n");
            scpi_send(client, "OUTP OFF\n");
            double r_equiv = v / i_meas;
            fprintf(stderr, "Розрахунковий еквівалентний опір дефекту: %.2f Ом\n", r_equiv);
            return false;
        }
    }

    printf("\nУспішний вихід на номінальний рівень напруги %.2f В.\n", target_voltage);
    SLEEP_MS(1000);
    double final_i = scpi_measure_current(client);
    printf("Усталений струм холостого ходу плати: %.2f мА (У межах норми)\n", final_i * 1000.0);
    return true;
}

int main(int argc, char *argv[]) {
    const char *psu_ip = (argc > 1) ? argv[1] : "192.168.1.105";
    int psu_port = 5025;

    ScpiClient client;
    if (!scpi_connect(&client, psu_ip, psu_port)) {
        return 1;
    }

    // Запуск: цільова напруга 3.3 В, апаратний захист 50 мА, програмний поріг спокою 35 мА
    bool ok = run_safe_bringup(&client, 3.30, 0.050, 0.035);

    if (!ok) {
        printf("Випробування зупинено через аварійний стан. Плата знеструмлена.\n");
    } else {
        printf("Плата успішно заживлена і готова до перевірки сигналів та підключення налагоджувача.\n");
    }

    scpi_disconnect(&client);
    return ok ? 0 : 1;
}
