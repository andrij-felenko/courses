#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

struct HttpResponse {
    char *data;
    size_t size;
};

static size_t write_memory_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    struct HttpResponse *resp = (struct HttpResponse *)userp;

    char *ptr = realloc(resp->data, resp->size + total_size + 1);
    if (!ptr) return 0; // Нестача оперативної пам'яті

    resp->data = ptr;
    memcpy(&(resp->data[resp->size]), contents, total_size);
    resp->size += total_size;
    resp->data[resp->size] = '\0';

    return total_size;
}

int main(void) {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    CURL *curl = curl_easy_init();

    if (!curl) {
        fprintf(stderr, "Помилка ініціалізації curl\n");
        return 1;
    }

    struct HttpResponse response = { .data = malloc(1), .size = 0 };
    struct curl_slist *headers = NULL;

    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "Accept: application/json");

    const char *payload = "{\"sensor\":\"BMP280\",\"pressure_hpa\":1013.25}";

    // Налаштування параметрів запиту (аналог PreparedRequest)
    curl_easy_setopt(curl, CURLOPT_URL, "https://httpbin.org/post");
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_memory_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 3L);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L); // allow_redirects=True

    CURLcode res = curl_easy_perform(curl);

    if (res == CURLE_OK) {
        long status_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status_code);
        printf("HTTP-статус: %ld, Отримано байтів: %zu\n", status_code, response.size);
    } else {
        fprintf(stderr, "Мережевий збій: %s\n", curl_easy_strerror(res));
    }

    // Ручне звільнення всіх низькорівневих ресурсів
    curl_slist_free_all(headers);
    free(response.data);
    curl_easy_cleanup(curl);
    curl_global_cleanup();

    return 0;
}
