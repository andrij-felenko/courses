#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/epoll.h>
#include <unistd.h>

int main(void)
{
    struct gpiod_chip *chip;
    struct gpiod_line_settings *settings;
    struct gpiod_line_config *line_cfg;
    struct gpiod_request_config *req_cfg;
    struct gpiod_line_request *request;
    struct epoll_event ev, events[1];
    int epoll_fd, req_fd;

    chip = gpiod_chip_open("/dev/gpiochip1");
    if (!chip) return EXIT_FAILURE;

    settings = gpiod_line_settings_new();
    gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);
    gpiod_line_settings_set_edge_detection(settings, GPIOD_LINE_EDGE_BOTH);

    line_cfg = gpiod_line_config_new();
    gpiod_line_config_add_line_settings(line_cfg, (const unsigned int[]){7}, 1, settings);

    req_cfg = gpiod_request_config_new();
    gpiod_request_config_set_consumer(req_cfg, "async_gpio_monitor");

    request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
    if (!request) return EXIT_FAILURE;

    req_fd = gpiod_line_request_get_fd(request);

    epoll_fd = epoll_create1(0);
    ev.events = EPOLLIN;
    ev.data.fd = req_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, req_fd, &ev);

    printf("Очікування фронтів сигналів на офсеті 7...\n");
    int nfds = epoll_wait(epoll_fd, events, 1, 5000); // 5 сек таймаут

    if (nfds > 0) {
        struct gpiod_edge_event_buffer *buffer = gpiod_edge_event_buffer_new(1);
        int ret = gpiod_line_request_read_edge_events(request, buffer, 1);
        if (ret > 0) {
            struct gpiod_edge_event *event = gpiod_edge_event_buffer_get_event(buffer, 0);
            enum gpiod_edge_event_type type = gpiod_edge_event_get_event_type(event);
            unsigned long long ts = gpiod_edge_event_get_timestamp_ns(event);
            printf("Отримано фронт: %s, Timestamp: %llu нс\n",
                   type == GPIOD_EDGE_EVENT_RISING_EDGE ? "RISING (Зростання)" : "FALLING (Спад)", ts);
        }
        gpiod_edge_event_buffer_free(buffer);
    }

    close(epoll_fd);
    gpiod_line_request_release(request);
    gpiod_line_settings_free(settings);
    gpiod_line_config_free(line_cfg);
    gpiod_request_config_free(req_cfg);
    gpiod_chip_close(chip);
    return EXIT_SUCCESS;
}
