#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <curl/curl.h>

/* Буфер для динамічного накопичення відповіді від HTTP-сервера OPA */
struct MemoryBuffer {
    char *response;
    size_t size;
};

/* Функція зворотного виклику для запису отриманих байтів у буфер */
static size_t write_callback(void *data, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    struct MemoryBuffer *mem = (struct MemoryBuffer *)userp;

    char *ptr = realloc(mem->response, mem->size + total_size + 1);
    if (!ptr) {
        return 0; // Помилка виділення пам'яті: libcurl перерве передачу
    }

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), data, total_size);
    mem->size += total_size;
    mem->response[mem->size] = '\0';

    return total_size;
}

/* Відправка запиту до точки ухвалення рішень OPA через локальний сокет */
bool opa_check_access(const char *opa_url, const char *json_payload) {
    CURL *curl = curl_easy_init();
    if (!curl) {
        return false;
    }

    struct MemoryBuffer chunk = { .response = malloc(1), .size = 0 };
    if (!chunk.response) {
        curl_easy_cleanup(curl);
        return false;
    }
    chunk.response[0] = '\0';

    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    curl_easy_setopt(curl, CURLOPT_URL, opa_url);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    
    // Жорсткий ліміт очікування відповіді: 500 мс
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, 500L);
    // Вимикаємо сигнали для повної потокобезпечності у багатопотокових серверах
    curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);

    CURLcode res = curl_easy_perform(curl);
    bool allowed = false;

    if (res == CURLE_OK) {
        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        if (http_code == 200 && chunk.response) {
            // Перевіряємо наявність поля "result":true у JSON-відповіді OPA
            if (strstr(chunk.response, "\"result\":true") != NULL) {
                allowed = true;
            }
        }
    }

    // Ручне звільнення всіх виділених системних ресурсів
    free(chunk.response);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    return allowed;
}

int main(void) {
    const char *url = "http://localhost:8181/v1/data/authz/allow";
    const char *payload = "{\"input\":{\"user\":{\"role\":\"admin\",\"mfa\":true},\"method\":\"POST\"}}";

    bool allowed = opa_check_access(url, payload);
    if (allowed) {
        printf("C Client: Доступ дозволено OPA PDP (200 OK)\n");
    } else {
        printf("C Client: Доступ відхилено OPA PDP (403 Forbidden)\n");
    }
    return 0;
}
