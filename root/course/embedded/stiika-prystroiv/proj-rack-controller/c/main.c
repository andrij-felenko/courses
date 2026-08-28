// Модуль керування слотом тестової стійки (C99 / POSIX)
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>
#include <sys/file.h>
#include <sys/select.h>
#include <sys/time.h>

#define SLOT_LOCK_DIR       "/tmp/dut-locks"
#define UART_CHUNK_SIZE     256
#define MAX_LOG_BUFFER      16384

typedef struct {
    int slot_id;
    int lock_fd;
    int uart_fd;
    char lock_path[64];
    char uart_path[64];
    char log_buffer[MAX_LOG_BUFFER];
    size_t log_length;
} rack_slot_t;

// Низькорівневе налаштування POSIX TTY в повністю "сирий" (Raw) режим
static bool configure_uart_raw(int fd, speed_t baud) {
    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        return false;
    }
    
    // Встановлення швидкості прийому та передачі
    cfsetospeed(&tty, baud);
    cfsetispeed(&tty, baud);
    
    // 8 біт даних, без парності, 1 стоп-біт, увімкнений прийом
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);
    
    // Відключення канонічного режиму, ехо та сигналів клавіатури
    tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    
    // Відключення програмного контролю потоку (XON/XOFF) та трансформації переведення рядків
    tty.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
    tty.c_oflag &= ~OPOST; // Сирий вивід без підстановки \r\n
    
    // Неблокуюче читання: повернути керування негайно, якщо буфер порожній
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;
    
    return tcsetattr(fd, TCSANOW, &tty) == 0;
}

// Захоплення слота через атомарне блокування файлу ядром Linux
bool rack_slot_acquire(rack_slot_t *slot, int slot_id) {
    slot->slot_id = slot_id;
    slot->lock_fd = -1;
    slot->uart_fd = -1;
    slot->log_length = 0;
    slot->log_buffer[0] = '\0';
    
    snprintf(slot->lock_path, sizeof(slot->lock_path), "%s/slot_%02d.lock", SLOT_LOCK_DIR, slot_id);
    snprintf(slot->uart_path, sizeof(slot->uart_path), "/dev/dut-slot-%02d-uart", slot_id);
    
    // Відкриття або створення файлу блокування
    slot->lock_fd = open(slot->lock_path, O_CREAT | O_RDWR, 0666);
    if (slot->lock_fd < 0) {
        return false;
    }
    
    // Спроба неблокуючого ексклюзивного блокування (LOCK_EX | LOCK_NB)
    if (flock(slot->lock_fd, LOCK_EX | LOCK_NB) != 0) {
        // Якщо файл уже захоплено іншим процесом, закриваємо дескриптор і повертаємо false
        close(slot->lock_fd);
        slot->lock_fd = -1;
        return false;
    }
    
    return true;
}

// Холодний рестарт плати зі збереженням раннього логу завантаження
bool rack_slot_power_cycle_and_listen(rack_slot_t *slot, uint32_t off_duration_ms) {
    // 1. Відкрити UART ДО увімкнення живлення
    if (slot->uart_fd < 0) {
        slot->uart_fd = open(slot->uart_path, O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (slot->uart_fd < 0) {
            return false;
        }
        if (!configure_uart_raw(slot->uart_fd, B115200)) {
            close(slot->uart_fd);
            slot->uart_fd = -1;
            return false;
        }
        // Очистити попередні залишкові байти
        tcflush(slot->uart_fd, TCIFLUSH);
    }
    
    // 2. Зняти живлення зі слота (VCC = 0)
    // Тут викликається низькорівнева функція керування силовим ключем
    usleep(off_duration_ms * 1000U);
    
    // 3. Подати живлення на слот (VCC = 1)
    // Силовий ключ плавно нарощує напругу
    usleep(25000U); // 25 мс очікування стабілізації живлення
    
    return true;
}

// Очікування появи цільового рядка в потоці консолі з таймаутом
bool rack_slot_expect(rack_slot_t *slot, const char *pattern, uint32_t timeout_ms) {
    if (slot->uart_fd < 0 || !pattern) {
        return false;
    }
    
    struct timeval tv_start, tv_now;
    gettimeofday(&tv_start, NULL);
    
    while (1) {
        gettimeofday(&tv_now, NULL);
        uint32_t elapsed_ms = (uint32_t)((tv_now.tv_sec - tv_start.tv_sec) * 1000 + 
                                         (tv_now.tv_usec - tv_start.tv_usec) / 1000);
        if (elapsed_ms >= timeout_ms) {
            return false; // Час вичерпано
        }
        
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(slot->uart_fd, &read_fds);
        
        struct timeval tv_poll;
        tv_poll.tv_sec = 0;
        tv_poll.tv_usec = 40000; // 40 мс квант очікування
        
        int ret = select(slot->uart_fd + 1, &read_fds, NULL, NULL, &tv_poll);
        if (ret > 0 && FD_ISSET(slot->uart_fd, &read_fds)) {
            char chunk[UART_CHUNK_SIZE];
            ssize_t bytes_read = read(slot->uart_fd, chunk, sizeof(chunk) - 1);
            if (bytes_read > 0) {
                chunk[bytes_read] = '\0';
                
                // Додавання до накопичувального логу
                if (slot->log_length + (size_t)bytes_read < MAX_LOG_BUFFER) {
                    memcpy(slot->log_buffer + slot->log_length, chunk, (size_t)bytes_read);
                    slot->log_length += (size_t)bytes_read;
                    slot->log_buffer[slot->log_length] = '\0';
                }
                
                // Пошук збігу з шаблоном
                if (strstr(slot->log_buffer, pattern) != NULL) {
                    return true; // Патерн знайдено!
                }
            }
        }
    }
}

// Звільнення дескрипторів та зняття блокування
void rack_slot_release(rack_slot_t *slot) {
    if (slot->uart_fd >= 0) {
        close(slot->uart_fd);
        slot->uart_fd = -1;
    }
    if (slot->lock_fd >= 0) {
        flock(slot->lock_fd, LOCK_UN);
        close(slot->lock_fd);
        slot->lock_fd = -1;
    }
}
