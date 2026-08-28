#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <expected>
#include <format>
#include <curl/curl.h>

class NativeHttpClient {
public:
    struct Response {
        long status_code{0};
        std::string body;
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

    NativeHttpClient() : curl_(curl_easy_init()) {
        if (!curl_) {
            throw std::runtime_error("Неможливо ініціалізувати CURL дескриптор");
        }
    }

    std::expected<Response, std::string> post_json(const std::string& url, const std::string& json_body, long timeout_sec = 10) {
        std::string response_buffer;
        SListPtr headers;

        // Безпечне додавання заголовків
        headers.reset(curl_slist_append(headers.release(), "Content-Type: application/json"));
        headers.reset(curl_slist_append(headers.release(), "Accept: application/json"));

        curl_easy_setopt(curl_.get(), CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl_.get(), CURLOPT_POSTFIELDS, json_body.c_str());
        curl_easy_setopt(curl_.get(), CURLOPT_HTTPHEADER, headers.get());
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEFUNCTION, &NativeHttpClient::writeCallback);
        curl_easy_setopt(curl_.get(), CURLOPT_WRITEDATA, &response_buffer);
        curl_easy_setopt(curl_.get(), CURLOPT_TIMEOUT, timeout_sec);
        curl_easy_setopt(curl_.get(), CURLOPT_CONNECTTIMEOUT, 3L);
        curl_easy_setopt(curl_.get(), CURLOPT_FOLLOWLOCATION, 1L);

        CURLcode res = curl_easy_perform(curl_.get());
        if (res != CURLE_OK) {
            return std::unexpected(std::format("Помилка запиту libcurl: {}", curl_easy_strerror(res)));
        }

        long status_code = 0;
        curl_easy_getinfo(curl_.get(), CURLINFO_RESPONSE_CODE, &status_code);

        return Response{
            .status_code = status_code,
            .body = std::move(response_buffer)
        };
    }

private:
    static size_t writeCallback(char* ptr, size_t size, size_t nmemb, void* userdata) {
        auto* buffer = static_cast<std::string*>(userdata);
        size_t total = size * nmemb;
        buffer->append(ptr, total);
        return total;
    }

    CurlPtr curl_;
};

int main() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    try {
        NativeHttpClient client;
        auto result = client.post_json("https://httpbin.org/post", "{\"sensor\":\"BMP280\",\"pressure_hpa\":1013.25}");
        if (result) {
            std::cout << std::format("Успіх! Статус: {}, Тіло: {} байтів\n", result->status_code, result->body.size());
        } else {
            std::cerr << result.error() << '\n';
        }
    } catch (const std::exception& e) {
        std::cerr << "Виняток: " << e.what() << '\n';
    }
    curl_global_cleanup();
    return 0;
}
