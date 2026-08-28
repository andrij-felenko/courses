#include <stdio.h>
#include <stdlib.h>

/* Контракт виводу на C через покажчик на функцію */
typedef struct OutputDevice {
    void (*write)(struct OutputDevice* self, const char* msg);
} OutputDevice;

static void console_write(OutputDevice* self, const char* msg) {
    (void)self;
    printf("[Консоль]: %s\n", msg);
}

static void file_write(OutputDevice* self, const char* msg) {
    (void)self;
    printf("[Файл]: %s\n", msg);
}

/* Композиція (HAS-A) */
typedef struct {
    OutputDevice* device;
} ApplicationLogger;

void logger_log(ApplicationLogger* self, const char* text) {
    if (self->device && self->device->write) {
        self->device->write(self->device, text);
    }
}

int main(void) {
    OutputDevice console_dev = { console_write };
    OutputDevice file_dev = { file_write };

    ApplicationLogger app_logger = { &console_dev };
    logger_log(&app_logger, "Старт системи");

    /* Зміна поведінки без перекомпіляції */
    app_logger.device = &file_dev;
    logger_log(&app_logger, "Дані збережено у звіт");

    return 0;
}
