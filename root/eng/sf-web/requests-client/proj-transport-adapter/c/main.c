#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <curl/curl.h>

struct MemoryBuffer {
    char *memory;
    size_t size;
};

static size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct MemoryBuffer *mem = (struct MemoryBuffer *)userp;
    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (!ptr) return 0;
    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

int send_resilient_request(CURL *curl, const char *url, int max_retries) {
    struct MemoryBuffer chunk = { .memory = malloc(1), .size = 0 };
    struct curl_slist *headers = NULL;
    
    char req_id[64];
    snprintf(req_id, sizeof(req_id), "X-Request-ID: req-%ld", (long)time(NULL));
    headers = curl_slist_append(headers, req_id);
    headers = curl_slist_append(headers, "X-Origin-Client: NativeClient-C");
    headers = curl_slist_append(headers, "User-Agent: NativeClient/1.0");

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 3L);

    int attempt = 0;
    CURLcode res = CURLE_OK;
    long http_code = 0;

    while (attempt <= max_retries) {
        chunk.size = 0;
        if (chunk.memory) chunk.memory[0] = '\0';

        res = curl_easy_perform(curl);
        if (res == CURLE_OK) {
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
            if (http_code < 500 && http_code != 429) {
                printf("[C Client] Успіх %ld (спроба %d): %zu байтів\n", http_code, attempt + 1, chunk.size);
                break;
            }
        }

        attempt++;
        if (attempt <= max_retries) {
            unsigned int delay_sec = 1 << attempt; // 2, 4, 8 секунд
            printf("[C Client] Помилка (res=%d, code=%ld). Очікування %u с перед спробою %d...\n",
                   res, http_code, delay_sec, attempt + 1);
            sleep(delay_sec);
        }
    }

    curl_slist_free_all(headers);
    free(chunk.memory);
    return (res == CURLE_OK && http_code < 400) ? 0 : -1;
}
