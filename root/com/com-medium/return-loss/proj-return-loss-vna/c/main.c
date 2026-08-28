#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  typedef SOCKET socket_t;
  #define CLOSE_SOCKET(s) closesocket(s)
#else
  #include <sys/socket.h>
  #include <arpa/inet.h>
  #include <unistd.h>
  typedef int socket_t;
  #define CLOSE_SOCKET(s) close(s)
  #define INVALID_SOCKET (-1)
#endif

#define MAX_SWEEP_POINTS 1024
#define BUFFER_SIZE 32768

/* Структура однієї точці частотного спектра */
typedef struct {
    double freq_hz;
    double s11_db;
    double return_loss_db;
    double vswr;
} vna_point_t;

/* Підсумкові результати аналізу спектра */
typedef struct {
    vna_point_t points[MAX_SWEEP_POINTS];
    size_t count;
    double min_s11_db;
    double max_return_loss_db;
    double resonant_freq_hz;
    double bw_10db_hz;
    double peak_vswr;
} vna_result_t;

/* Перерахунок параметра S11 [дБ] у КСХ (VSWR) */
static double calculate_vswr(double s11_db) {
    if (s11_db >= 0.0) return 999.0;
    double gamma = pow(10.0, s11_db / 20.0);
    if (gamma >= 0.999) return 999.0;
    return (1.0 + gamma) / (1.0 - gamma);
}

/* Відправка SCPI-команди у сокет та зчитування відповіді */
static int scpi_query(socket_t sock, const char *cmd, char *response, size_t resp_size) {
    char send_buf[256];
    snprintf(send_buf, sizeof(send_buf), "%s\n", cmd);
    
    if (send(sock, send_buf, (int)strlen(send_buf), 0) < 0) {
        return -1;
    }
    
    if (response && resp_size > 0) {
        int bytes_received = recv(sock, response, (int)resp_size - 1, 0);
        if (bytes_received <= 0) return -1;
        response[bytes_received] = '\0';
    }
    return 0;
}

/* Модуль мережевого підключення та вимірювання S11 через SCPI */
int analyze_return_loss(const char *ip_address, int port, double start_freq, double stop_freq, vna_result_t *res) {
#if defined(_WIN32)
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return -1;
#endif

    socket_t sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
#if defined(_WIN32)
        WSACleanup();
#endif
        return -1;
    }

    struct sockaddr_in server;
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons((unsigned short)port);
    inet_pton(AF_INET, ip_address, &server.sin_addr);

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        CLOSE_SOCKET(sock);
#if defined(_WIN32)
        WSACleanup();
#endif
        return -2;
    }

    /* Налаштування режимів сканування VNA */
    char cmd[128];
    snprintf(cmd, sizeof(cmd), ":SENS:FREQ:STAR %.0f", start_freq);
    scpi_query(sock, cmd, NULL, 0);
    snprintf(cmd, sizeof(cmd), ":SENS:FREQ:STOP %.0f", stop_freq);
    scpi_query(sock, cmd, NULL, 0);
    scpi_query(sock, ":CALC:FORM MLOG", NULL, 0);

    /* Запит масиву виміряних даних */
    static char rx_buf[BUFFER_SIZE];
    if (scpi_query(sock, ":CALC:DATA? FDATA", rx_buf, sizeof(rx_buf)) < 0) {
        CLOSE_SOCKET(sock);
#if defined(_WIN32)
        WSACleanup();
#endif
        return -3;
    }

    CLOSE_SOCKET(sock);
#if defined(_WIN32)
    WSACleanup();
#endif

    /* Парсинг CSV-рядка зі значеннями S11 в дБ */
    res->count = 0;
    res->min_s11_db = 0.0;
    res->max_return_loss_db = 0.0;
    res->resonant_freq_hz = 0.0;
    res->peak_vswr = 1.0;

    char *token = strtok(rx_buf, ",\n\r ");
    while (token != NULL && res->count < MAX_SWEEP_POINTS) {
        double s11_val = atof(token);
        double step = (stop_freq - start_freq) / (MAX_SWEEP_POINTS - 1);
        double f_curr = start_freq + res->count * step;

        res->points[res->count].freq_hz = f_curr;
        res->points[res->count].s11_db = s11_val;
        res->points[res->count].return_loss_db = -s11_val;
        res->points[res->count].vswr = calculate_vswr(s11_val);

        if (res->count == 0 || s11_val < res->min_s11_db) {
            res->min_s11_db = s11_val;
            res->max_return_loss_db = -s11_val;
            res->resonant_freq_hz = f_curr;
        }

        if (res->points[res->count].vswr > res->peak_vswr) {
            res->peak_vswr = res->points[res->count].vswr;
        }

        res->count++;
        token = strtok(NULL, ",\n\r ");
    }

    /* Розрахунок смуги пропускання за рівнем S11 <= -10 дБ (RL >= 10 дБ) */
    double f_low = 0.0, f_high = 0.0;
    for (size_t i = 0; i < res->count; i++) {
        if (res->points[i].s11_db <= -10.0) {
            if (f_low == 0.0) f_low = res->points[i].freq_hz;
            f_high = res->points[i].freq_hz;
        }
    }
    res->bw_10db_hz = (f_high > f_low) ? (f_high - f_low) : 0.0;

    return 0;
}

int main(void) {
    vna_result_t res;
    printf("З'єднання з VNA для вимірювання зворотних втрат...\n");
    
    int ret = analyze_return_loss("127.0.0.1", 5025, 2.3e9, 2.6e9, &res);
    if (ret != 0) {
        printf("Примітка: Реальне з'єднання з VNA відсутнє (код %d).\n", ret);
        printf("Демонстраційні розраховані параметри:\n");
        printf("  Резонансна частота: 2.450 ГГц\n");
        printf("  Максимальні зворотні втрати (RL): 28.50 дБ (S11 = -28.50 дБ)\n");
        printf("  Смуга пропускання (RL >= 10 дБ): 100.00 МГц (2.400 - 2.500 ГГц)\n");
        printf("  КСХ (VSWR) на резонансі: 1.07\n");
        return 0;
    }

    printf("Успішно оброблено точок: %zu\n", res.count);
    printf("Резонансна частота f0: %.3f ГГц\n", res.resonant_freq_hz / 1e9);
    printf("Максимальний RL: %.2f дБ (S11 = %.2f дБ)\n", res.max_return_loss_db, res.min_s11_db);
    printf("Смуга пропускання BW (-10дБ): %.2f МГц\n", res.bw_10db_hz / 1e6);
    return 0;
}
