#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <thread>
#include <random>
#include <format>
#include <expected>
#include <curl/curl.h>

class ResilientHttpClient {
public:
    struct Response {
        long status_code{0};
        std::string body;
        double elapsed_ms{0.0};
    };

    struct SListDeleter {
        void operator()(curl_slist* list) const noexcept {
            if (list) curl_slist_free_all(list);
        }
    };
    using SListPtr = std::unique_ptr<curl_slist, SListDeleter>;

    struct CurlDeleter {
        void operator()(CURL* handle) const noexcept {
            if (handle) curl_easy_cleanup(handle);
        }
    };
    using CurlPtr = std::unique_ptr<CURL, CurlDeleter>;

    explicit ResilientHttpClient(std::string client_name, int max_retries = 3)
        : client_name_(std::move(client_name)), max_retries_(max_retries), curl_(curl_easy_init()) {
        if (!curl_) {
            throw std::runtime_error("Не вдалося ініціалізувати дескриптор libcurl");
        }
    }

    std::expected<Response, std::string> get(const std::string& url, int timeout_sec = 10) {
        std::string buffer;
        SListPtr headers;

        std::string req_id = std::format("X-Request-ID: cpp-{}", std::chrono::steady_clock::now().time_since_epoch().count());
        headers.reset(curl_slist_append(headers.release(), req_id.c_str()));
        headers.reset(curl_slist_append(headers.release(), ("X-Origin-Client: " + client_name_).c_str()));

        curl_easy_setopt(curl_.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl_.get(), CURLOPT_HTTPHEADER, headers.get());
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEFUNCTION, &ResilientHttpClient::writeCallback);
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEDATA, &buffer);
        curl_easy_setopt(curl_.get(), CURLOPT_TIMEOUT, static_cast<long>(timeout_sec));
        curl_easy_setopt(curl_.get(), CURLOPT_CONNECTTIMEOUT, 3L);
        curl_easy_setopt(curl_.get(), CURLOPT_TCP_NODELAY, 1L);

        int attempt = 0;
        CURLcode res = CURLE_OK;
        long http_code = 0;
        auto start_time = std::chrono::steady_clock::now();

        while (attempt <= max_retries_) {
            buffer.clear();
            res = curl_easy_perform(curl_.get());

            if (res == CURLE_OK) {
                curl_easy_getinfo(curl_.get(), CURLINFO_RESPONSE_CODE, &http_code);
                if (http_code < 500 && http_code != 429) {
                    auto end_time = std::chrono::steady_clock::now();
                    double elapsed = std::chrono::duration<double, std::milli>(end_time - start_time).count();
                    return Response{
                        .status_code = http_code,
                        .body = std::move(buffer),
                        .elapsed_ms = elapsed
                    };
                }
            }

            attempt++;
            if (attempt <= max_retries_) {
                auto backoff = std::chrono::milliseconds(200 * (1 << attempt));
                std::this_thread::sleep_for(backoff);
            }
        }

        return std::unexpected(std::format("Помилка після {} спроб: curl_code={}, http_code={}",
                                           attempt, static_cast<int>(res), http_code));
    }

private:
    static size_t writeCallback(char* ptr, size_t size, size_t nmemb, void* userdata) {
        auto* str = static_cast<std::string*>(userdata);
        size_t total = size * nmemb;
        str->append(ptr, total);
        return total;
    }

    std::string client_name_;
    int max_retries_;
    CurlPtr curl_;
};
