#pragma once

#include "esp_err.h"
#include "esp_http_server.h"

/*
 * Запускає вбудований веб-сервер порталу: сторінку майстра з Flash,
 * REST-обробники сканування й збереження та універсальний перехоплювач,
 * що відповідає 302-м на будь-який невідомий шлях.
 */
esp_err_t http_server_init(httpd_handle_t *out_server);

/* Зупиняє сервер і звільняє його сокети. */
void http_server_stop(httpd_handle_t server);
