#include <curl/curl.h>
#include <memory>
#include <stdexcept>

struct CurlDeleter {
    void operator()(CURL* handle) const noexcept {
        if (handle) curl_easy_cleanup(handle);
    }
};

void fetch_url(const char* url) {
    std::unique_ptr<CURL, CurlDeleter> curl(curl_easy_init());
    if (!curl) throw std::runtime_error("Не вдалося ініціалізувати curl");

    curl_easy_setopt(curl.get(), CURLOPT_URL, url);
    curl_easy_setopt(curl.get(), CURLOPT_HAPPY_EYEBALLS_TIMEOUT_MS, 250L);
    curl_easy_setopt(curl.get(), CURLOPT_IPRESOLVE, CURL_IPRESOLVE_WHATEVER);
    curl_easy_setopt(curl.get(), CURLOPT_CONNECTTIMEOUT_MS, 10000L);

    CURLcode res = curl_easy_perform(curl.get());
    if (res != CURLE_OK) {
        throw std::runtime_error(curl_easy_strerror(res));
    }
}
