#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

/* Допоміжна функція відправки SCPI-команди */
int scpi_send(int sock, const char* cmd) {
    int len = (int)strlen(cmd);
    int sent = send(sock, cmd, len, 0);
    return (sent == len) ? 0 : -1;
}

/* 
 * Зчитування текстової відповіді на SCPI-запит
 */
int scpi_query_str(int sock, const char* query, char* out_buf, int max_len) {
    if (scpi_send(sock, query) < 0) return -1;

    int bytes = recv(sock, out_buf, max_len - 1, 0);
    if (bytes <= 0) return -2;

    out_buf[bytes] = '\0';
    return bytes;
}

/*
 * Комплексна функція налаштування TDR та зчитування траси
 */
int tdr_scpi_read_impedance(const char* ip_address, int port,
                             double span_ns, double vf_factor,
                             float* out_trace_ohm, int max_points) {
#if defined(_WIN32)
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) return -1;
#endif

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
#if defined(_WIN32)
        WSACleanup();
#endif
        return -2;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);
    inet_pton(AF_INET, ip_address, &serv_addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
#if defined(_WIN32)
        closesocket(sock);
        WSACleanup();
#else
        close(sock);
#endif
        return -3;
    }

    /* 1. Ідентифікація приладу */
    char idn[256];
    scpi_query_str(sock, "*IDN?\n", idn, sizeof(idn));
    printf("З'єднано з приладом: %s", idn);

    /* 2. Конфігурація підсистеми TDR */
    scpi_send(sock, ":SENS1:TDR:STAT ON\n");
    scpi_send(sock, ":SENS1:TDR:PULS:AMPL 0.200\n");
    
    char cmd_buf[128];
    snprintf(cmd_buf, sizeof(cmd_buf), ":TIM:SPAN %.9e\n", span_ns * 1e-9);
    scpi_send(sock, cmd_buf);

    snprintf(cmd_buf, sizeof(cmd_buf), ":CALC1:TDR:VFACT %.4f\n", vf_factor);
    scpi_send(sock, cmd_buf);

    scpi_send(sock, ":CALC1:TDR:UNIT IMP\n");
    scpi_send(sock, ":FORM:DATA ASCII\n");

    /* 3. Запит траси даних */
    scpi_send(sock, ":TRAC:DATA? TRACE1\n");

    char rx_chunk[2048];
    int count = 0;
    int bytes_read = 0;

    while ((bytes_read = recv(sock, rx_chunk, sizeof(rx_chunk) - 1, 0)) > 0 && count < max_points) {
        rx_chunk[bytes_read] = '\0';
        char* token = strtok(rx_chunk, ",\n\r");
        while (token && count < max_points) {
            out_trace_ohm[count++] = (float)atof(token);
            token = strtok(NULL, ",\n\r");
        }
        if (bytes_read < (int)sizeof(rx_chunk) - 1) break;
    }

    /* 4. Завершення сесії */
    scpi_send(sock, ":SENS1:TDR:STAT OFF\n");

#if defined(_WIN32)
    closesocket(sock);
    WSACleanup();
#else
    close(sock);
#endif

    return count;
}
