/* Приклад обробки EMSGSIZE та отримання актуального PMTU у сокеті */
int sock = socket(AF_INET, SOCK_DGRAM, 0);
if (sock < 0) return -1;

int pmtu_mode = IP_PMTUDISC_DO;
setsockopt(sock, IPPROTO_IP, IP_MTU_DISCOVER, &pmtu_mode, sizeof(pmtu_mode));

ssize_t sent = sendto(sock, large_buffer, 2000, 0, (struct sockaddr*)&dst, sizeof(dst));
if (sent < 0 && errno == EMSGSIZE) {
    /* Запитуємо у ядра актуальний кешований Path MTU для цього сокета */
    int current_pmtu = 0;
    socklen_t optlen = sizeof(current_pmtu);
    if (getsockopt(sock, IPPROTO_IP, IP_MTU, &current_pmtu, &optlen) == 0) {
        /* Зменшуємо розмір блоку передачі на рівні застосунку */
        int safe_payload_len = current_pmtu - 20 - 8; /* IP (20B) + UDP (8B) */
        sendto(sock, large_buffer, safe_payload_len, 0, (struct sockaddr*)&dst, sizeof(dst));
    }
}
close(sock);
