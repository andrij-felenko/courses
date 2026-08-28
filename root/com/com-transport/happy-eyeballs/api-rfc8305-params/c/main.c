#include <curl/curl.h>

CURL *curl = curl_easy_init();
if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "https://example.com");

    /* Встановлення затримки між спробами Happy Eyeballs (за замовчуванням 200 мс) */
    curl_easy_setopt(curl, CURLOPT_HAPPY_EYEBALLS_TIMEOUT_MS, 250L);

    /* Дозволити використання обох родин адрес (CURL_IPRESOLVE_WHATEVER) */
    curl_easy_setopt(curl, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_WHATEVER);

    /* Загальний таймаут на встановлення TCP-з'єднання */
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT_MS, 10000L);

    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);
}
