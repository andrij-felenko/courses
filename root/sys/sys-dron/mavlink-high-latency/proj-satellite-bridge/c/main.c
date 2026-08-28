#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <time.h>
#include <sys/select.h>

#define SBD_MAX_PAYLOAD_SIZE 340
#define SBD_MIN_RATE_INTERVAL_SEC 20.0f
#define SBD_TOKEN_BUCKET_CAPACITY 2.0f

typedef enum {
    SBD_FSM_IDLE,
    SBD_FSM_CHECK_SIGNAL,
    SBD_FSM_WRITE_PAYLOAD,
    SBD_FSM_EXECUTE_SBDIX,
    SBD_FSM_READ_INCOMING_CMD,
    SBD_FSM_CLEAR_BUFFER,
    SBD_FSM_ERROR_BACKOFF
} sbd_fsm_state_t;

typedef struct {
    int modem_uart_fd;
    int fcu_uart_fd;
    sbd_fsm_state_t state;
    
    // Маркерний кошик
    double tokens;
    time_t last_token_update;
    
    // Буфери передачі та прийому
    uint8_t mo_buffer[SBD_MAX_PAYLOAD_SIZE];
    size_t mo_len;
    uint8_t mt_buffer[SBD_MAX_PAYLOAD_SIZE];
    size_t mt_len;
    
    // Статистика
    uint32_t tx_success_count;
    uint32_t tx_fail_count;
    time_t state_entry_time;
} satellite_bridge_t;

int bridge_init_serial_port(const char *device_path, int speed_constant) {
    int fd = open(device_path, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) return -1;

    struct termios tty;
    memset(&tty, 0, sizeof(tty));
    if (tcgetattr(fd, &tty) != 0) {
        close(fd);
        return -1;
    }

    cfsetispeed(&tty, B19200);
    cfsetospeed(&tty, B19200);

    tty.c_cflag |= (CLOCAL | CREAD | CS8 | CRTSCTS); // 8N1 + Hardware Flow Control
    tty.c_cflag &= ~(PARENB | CSTOPB | CSIZE);
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF | IXANY);
    tty.c_oflag &= ~OPOST;
    tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 5; // 500 мс таймаут

    tcflush(fd, TCIFLUSH);
    tcsetattr(fd, TCSANOW, &tty);
    return fd;
}

void bridge_update_tokens(satellite_bridge_t *br) {
    time_t now = time(NULL);
    double elapsed = difftime(now, br->last_token_update);
    br->tokens += elapsed / SBD_MIN_RATE_INTERVAL_SEC;
    if (br->tokens > SBD_TOKEN_BUCKET_CAPACITY) {
        br->tokens = SBD_TOKEN_BUCKET_CAPACITY;
    }
    br->last_token_update = now;
}

bool bridge_enqueue_high_latency_frame(satellite_bridge_t *br, const uint8_t *frame_bytes, size_t len) {
    if (len == 0 || len > SBD_MAX_PAYLOAD_SIZE) return false;
    
    // Перезапис буфера найсвіжішим кадром
    memcpy(br->mo_buffer, frame_bytes, len);
    br->mo_len = len;
    return true;
}

void bridge_process_step(satellite_bridge_t *br) {
    char at_cmd[64];
    bridge_update_tokens(br);

    switch (br->state) {
        case SBD_FSM_IDLE:
            if (br->mo_len > 0 && br->tokens >= 1.0) {
                br->state = SBD_FSM_CHECK_SIGNAL;
                br->state_entry_time = time(NULL);
                write(br->modem_uart_fd, "AT+CSQ\r", 7);
            }
            break;

        case SBD_FSM_CHECK_SIGNAL:
            // У спрощеному лінійному вигляді переходимо до запису
            br->state = SBD_FSM_WRITE_PAYLOAD;
            br->state_entry_time = time(NULL);
            snprintf(at_cmd, sizeof(at_cmd), "AT+SBDWB=%zu\r", br->mo_len);
            write(br->modem_uart_fd, at_cmd, strlen(at_cmd));
            break;

        case SBD_FSM_WRITE_PAYLOAD: {
            uint16_t checksum = 0;
            for (size_t i = 0; i < br->mo_len; i++) checksum += br->mo_buffer[i];
            
            uint8_t cs_payload[2] = { (uint8_t)(checksum >> 8), (uint8_t)(checksum & 0xFF) };
            write(br->modem_uart_fd, br->mo_buffer, br->mo_len);
            write(br->modem_uart_fd, cs_payload, 2);
            
            br->state = SBD_FSM_EXECUTE_SBDIX;
            br->state_entry_time = time(NULL);
            write(br->modem_uart_fd, "AT+SBDIX\r", 9);
            break;
        }

        case SBD_FSM_EXECUTE_SBDIX:
            // Успішна сесія: списуємо 1 токен
            br->tokens -= 1.0;
            br->tx_success_count++;
            br->mo_len = 0; // Очищення відправленого
            br->state = SBD_FSM_CLEAR_BUFFER;
            write(br->modem_uart_fd, "AT+SBDD0\r", 9);
            break;

        case SBD_FSM_CLEAR_BUFFER:
            br->state = SBD_FSM_IDLE;
            break;

        case SBD_FSM_ERROR_BACKOFF:
            if (difftime(time(NULL), br->state_entry_time) > 10.0) {
                br->state = SBD_FSM_IDLE;
            }
            break;

        default:
            br->state = SBD_FSM_IDLE;
            break;
    }
}
