#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <stdint.h>

#define PORT 8080
#define CHUNK_SIZE 1024
#define BUFFER_SIZE 4096

double get_time() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

void handle_client(int client_sock) {
    uint8_t buffer[BUFFER_SIZE];
    uint8_t chunk_buffer[CHUNK_SIZE];
    int chunk_pos = 0;
    
    uint64_t total_bytes = 0;
    uint32_t expected_seq = 0;
    
    double last_report_time = get_time();
    uint64_t bytes_since_report = 0;
    
    while (1) {
        ssize_t bytes_read = recv(client_sock, buffer, sizeof(buffer), 0);
        if (bytes_read <= 0) break;
        
        for (ssize_t i = 0; i < bytes_read; i++) {
            chunk_buffer[chunk_pos++] = buffer[i];
            
            // Якщо накопичили повний блок
            if (chunk_pos == CHUNK_SIZE) {
                uint8_t calculated_checksum = 0;
                for (int j = 0; j < CHUNK_SIZE - 1; j++) {
                    calculated_checksum ^= chunk_buffer[j];
                }
                
                if (calculated_checksum != chunk_buffer[CHUNK_SIZE - 1]) {
                    printf("Помилка КС! Очікувано: %u, Отримано: %u\n", calculated_checksum, chunk_buffer[CHUNK_SIZE - 1]);
                }
                
                uint32_t seq;
                memcpy(&seq, chunk_buffer, sizeof(seq));
                
                if (seq != expected_seq) {
                    printf("Втрата пакетів! Очікуваний seq: %u, Отриманий: %u\n", expected_seq, seq);
                    expected_seq = seq;
                }
                
                expected_seq++;
                total_bytes += CHUNK_SIZE;
                bytes_since_report += CHUNK_SIZE;
                chunk_pos = 0;
                
                double current_time = get_time();
                if (current_time - last_report_time >= 1.0) {
                    double speed_kb = (bytes_since_report / 1024.0) / (current_time - last_report_time);
                    printf("Отримано: %.2f KB, Швидкість: %.2f KB/s\n", total_bytes / 1024.0, speed_kb);
                    last_report_time = current_time;
                    bytes_since_report = 0;
                }
            }
        }
    }
    close(client_sock);
}

int main() {
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) {
        perror("socket");
        return 1;
    }
    
    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    if (bind(server_sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        return 1;
    }
    
    if (listen(server_sock, 5) < 0) {
        perror("listen");
        return 1;
    }
    
    printf("Сервер слухає на порту %d...\n", PORT);
    
    while (1) {
        int client_sock = accept(server_sock, NULL, NULL);
        if (client_sock >= 0) {
            printf("Нове з'єднання\n");
            handle_client(client_sock);
            printf("Клієнт відключився\n");
        }
    }
    
    close(server_sock);
    return 0;
}
