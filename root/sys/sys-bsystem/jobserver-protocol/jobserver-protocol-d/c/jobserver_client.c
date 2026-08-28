/* jobserver_client.c — POSIX & Windows C Client */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#endif

typedef enum {
    JS_MODE_NONE,
    JS_MODE_PIPE,
    JS_MODE_FIFO,
    JS_MODE_SEMAPHORE
} jobserver_mode_t;

typedef struct {
    jobserver_mode_t mode;
    int has_implicit_token;
#if defined(_WIN32)
    HANDLE sem_handle;
#else
    int read_fd;
    int write_fd;
#endif
} jobserver_client_t;

/* Розбір змінної MAKEFLAGS та ініціалізація клієнта */
int jobserver_init(jobserver_client_t *js) {
    js->mode = JS_MODE_NONE;
    js->has_implicit_token = 1; /* Власний слот виконання */

    const char *makeflags = getenv("MAKEFLAGS");
    if (!makeflags) {
        makeflags = getenv("MFLAGS");
    }
    if (!makeflags) {
        return 0; /* Працюємо в автономному режимі з 1 неявним слотом */
    }

    /* Пошук --jobserver-auth= або --jobserver-fds= */
    const char *auth = strstr(makeflags, "--jobserver-auth=");
    if (!auth) {
        auth = strstr(makeflags, "--jobserver-fds=");
    }
    if (!auth) {
        return 0;
    }

    const char *val = strchr(auth, '=') + 1;

#if defined(_WIN32)
    /* Windows Semaphore: --jobserver-auth=semaphore_name або fifo: / semaphore: */
    char sem_name[256];
    if (strncmp(val, "semaphore:", 10) == 0) {
        val += 10;
    }
    size_t len = strcspn(val, " \t\n");
    if (len >= sizeof(sem_name)) len = sizeof(sem_name) - 1;
    strncpy(sem_name, val, len);
    sem_name[len] = '\0';

    js->sem_handle = OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, sem_name);
    if (js->sem_handle != NULL) {
        js->mode = JS_MODE_SEMAPHORE;
        return 1;
    }
#else
    /* POSIX FIFO: --jobserver-auth=fifo:/path/to/fifo */
    if (strncmp(val, "fifo:", 5) == 0) {
        const char *path_start = val + 5;
        char fifo_path[512];
        size_t len = strcspn(path_start, " \t\n");
        if (len >= sizeof(fifo_path)) len = sizeof(fifo_path) - 1;
        strncpy(fifo_path, path_start, len);
        fifo_path[len] = '\0';

        int fd = open(fifo_path, O_RDWR | O_CLOEXEC | O_NONBLOCK);
        if (fd >= 0) {
            js->read_fd = fd;
            js->write_fd = fd;
            js->mode = JS_MODE_FIFO;
            return 1;
        }
    } else {
        /* Класичні дескриптори: --jobserver-auth=R,W */
        int rfd = -1, wfd = -1;
        if (sscanf(val, "%d,%d", &rfd, &wfd) == 2) {
            /* Переведення дескриптора читання в неблокувальний режим */
            int flags = fcntl(rfd, F_GETFL, 0);
            if (flags >= 0) {
                fcntl(rfd, F_SETFL, flags | O_NONBLOCK);
                js->read_fd = rfd;
                js->write_fd = wfd;
                js->mode = JS_MODE_PIPE;
                return 1;
            }
        }
    }
#endif
    return 0;
}

/* Спроба отримати токен для запуску задачі (1 = успіх, 0 = немає доступних токенів) */
int jobserver_acquire(jobserver_client_t *js, char *out_token) {
    /* 1. Спершу використовуємо свій неявний слот */
    if (js->has_implicit_token) {
        js->has_implicit_token = 0;
        *out_token = '+';
        return 1;
    }

    /* 2. Якщо неявний слот зайнятий — запитуємо зовнішній токен */
    if (js->mode == JS_MODE_NONE) {
        return 0; /* Немає підключення до пулу, додаткові задачі заборонені */
    }

#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE) {
        /* Неблокувальне опитування семафора */
        DWORD res = WaitForSingleObject(js->sem_handle, 0);
        if (res == WAIT_OBJECT_0) {
            *out_token = '+';
            return 1;
        }
        return 0;
    }
#else
    if (js->mode == JS_MODE_PIPE || js->mode == JS_MODE_FIFO) {
        char buf = 0;
        ssize_t n = read(js->read_fd, &buf, 1);
        if (n == 1) {
            *out_token = buf;
            return 1;
        }
        if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            return 0; /* Токенів немає в наявності */
        }
    }
#endif
    return 0;
}

/* Повернення токена після завершення задачі */
void jobserver_release(jobserver_client_t *js, char token) {
    /* Якщо неявний слот вільний — повертаємо його */
    if (!js->has_implicit_token) {
        js->has_implicit_token = 1;
        return;
    }

    if (js->mode == JS_MODE_NONE) {
        return;
    }

#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE) {
        ReleaseSemaphore(js->sem_handle, 1, NULL);
    }
#else
    if (js->mode == JS_MODE_PIPE || js->mode == JS_MODE_FIFO) {
        ssize_t written = 0;
        while (written <= 0) {
            written = write(js->write_fd, &token, 1);
            if (written < 0 && errno == EINTR) {
                continue; /* Повтор при перериванні сигналом */
            }
            break;
        }
    }
#endif
}

/* Закриття клієнта */
void jobserver_close(jobserver_client_t *js) {
#if defined(_WIN32)
    if (js->mode == JS_MODE_SEMAPHORE && js->sem_handle) {
        CloseHandle(js->sem_handle);
        js->sem_handle = NULL;
    }
#else
    if (js->mode == JS_MODE_FIFO && js->read_fd >= 0) {
        close(js->read_fd);
        js->read_fd = -1;
        js->write_fd = -1;
    }
#endif
    js->mode = JS_MODE_NONE;
}
