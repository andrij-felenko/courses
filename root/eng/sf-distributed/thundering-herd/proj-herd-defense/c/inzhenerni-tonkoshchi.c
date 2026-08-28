/* C11 implementation: client connection loop with decorrelated jitter */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

typedef struct {
    double base_sec;
    double max_sec;
    double prev_backoff_sec;
    unsigned int seed;
} JitterBackoff;

void jitter_init(JitterBackoff *jb, double base_sec, double max_sec) {
    jb->base_sec = base_sec;
    jb->max_sec = max_sec;
    jb->prev_backoff_sec = base_sec;
    jb->seed = (unsigned int)(time(NULL) ^ getpid());
}

double jitter_next(JitterBackoff *jb) {
    double low = jb->base_sec;
    double high = jb->prev_backoff_sec * 3.0;
    if (high < low) {
        high = low;
    }
    
    /* Uniform random in [low, high] */
    double r = (double)rand_r(&jb->seed) / (double)RAND_MAX;
    double sleep_time = low + r * (high - low);
    
    if (sleep_time > jb->max_sec) {
        sleep_time = jb->max_sec;
    }
    
    jb->prev_backoff_sec = sleep_time;
    return sleep_time;
}

int connect_with_herd_protection(const char *ip, int port, int max_attempts) {
    JitterBackoff backoff;
    jitter_init(&backoff, 0.5, 30.0); /* base 500ms, max 30s */
    
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        return -1;
    }

    for (int attempt = 1; attempt <= max_attempts; ++attempt) {
        int sock_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (sock_fd < 0) {
            return -1;
        }

        if (connect(sock_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == 0) {
            printf("[Client] Connected on attempt %d\n", attempt);
            return sock_fd;
        }

        close(sock_fd);
        double delay = jitter_next(&backoff);
        printf("[Client] Attempt %d failed. Jittered sleep: %.3f s\n", attempt, delay);
        
        struct timespec ts;
        ts.tv_sec = (time_t)delay;
        ts.tv_nsec = (long)((delay - (time_t)delay) * 1e9);
        nanosleep(&ts, NULL);
    }

    return -1; /* Exceeded max attempts */
}
