#include <iostream>
#include <string>
#include <string_view>
#include <cstdlib>
#include <format>
#include <chrono>
#include <curl/curl.h>

// Допоміжний клас RAII для керування дескриптором libcurl
class CurlHandle {
public:
    CurlHandle() : handle_(curl_easy_init()) {
        if (!handle_) throw std::runtime_error("Не вдалося ініціалізувати CURL");
    }
    ~CurlHandle() { if (handle_) curl_easy_cleanup(handle_); }
    CURL* get() const noexcept { return handle_; }

    CurlHandle(const CurlHandle&) = delete;
    CurlHandle& operator=(const CurlHandle&) = delete;
private:
    CURL* handle_;
};

// Зворотний виклик для запису тіла відповіді
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    auto* s = static_cast<std::string*>(userp);
    s->append(static_cast<char*>(contents), size * nmemb);
    return size * nmemb;
}

// Зворотний виклик для парсингу заголовків відповіді
static size_t HeaderCallback(char* buffer, size_t size, size_t nitems, void* userp) {
    size_t total = size * nitems;
    std::string_view header(buffer, total);
    auto* req_id = static_cast<std::string*>(userp);
    
    constexpr std::string_view target = "lambda-runtime-aws-request-id:";
    if (header.size() >= target.size()) {
        // Порівняння без урахування регістру перших байтів
        bool match = true;
        for (size_t i = 0; i < target.size(); ++i) {
            if (std::tolower(header[i]) != target[i]) { match = false; break; }
        }
        if (match) {
            auto val = header.substr(target.size());
            // Видалення пробілів та символів переносу рядка
            while (!val.empty() && (val.front() == ' ' || val.front() == '\t')) val.remove_prefix(1);
            while (!val.empty() && (val.back() == '\r' || val.back() == '\n' || val.back() == ' ')) val.remove_suffix(1);
            *req_id = std::string(val);
        }
    }
    return total;
}

// Бізнес-логіка обробника події
std::string HandleEvent(std::string_view payload, std::string_view request_id) {
    // Демонстраційна обробка: генерація відповіді JSON
    return std::format(R"({{"status":"success","request_id":"{}","processed_bytes":{}}})", 
                       request_id, payload.size());
}

int main() {
    // 1. Фаза Init: зчитування адреси Runtime API
    const char* api_env = std::getenv("AWS_LAMBDA_RUNTIME_API");
    if (!api_env) {
        std::cerr << "Помилка: AWS_LAMBDA_RUNTIME_API не встановлено\n";
        return 1;
    }
    const std::string runtime_api = api_env;
    const std::string next_url = std::format("http://{}/2018-06-01/runtime/invocation/next", runtime_api);

    curl_global_init(CURL_GLOBAL_ALL);

    // 2. Нескінченний цикл фази Invoke
    while (true) {
        CurlHandle curl;
        std::string response_body;
        std::string request_id;

        curl_easy_setopt(curl.get(), CURLOPT_URL, next_url.c_str());
        curl_easy_setopt(curl.get(), CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl.get(), CURLOPT_WRITEDATA, &response_body);
        curl_easy_setopt(curl.get(), CURLOPT_HEADERFUNCTION, HeaderCallback);
        curl_easy_setopt(curl.get(), CURLOPT_HEADERDATA, &request_id);

        CURLcode res = curl_easy_perform(curl.get());
        if (res != CURLE_OK || request_id.empty()) {
            std::cerr << "Помилка отримання події: " << curl_easy_strerror(res) << "\n";
            continue;
        }

        // Виклик користувацького обробника
        std::string result = HandleEvent(response_body, request_id);

        // 3. Відправка результату назад у Runtime API
        std::string post_url = std::format("http://{}/2018-06-01/runtime/invocation/{}/response", 
                                           runtime_api, request_id);
        
        CurlHandle post_curl;
        curl_easy_setopt(post_curl.get(), CURLOPT_URL, post_url.c_str());
        curl_easy_setopt(post_curl.get(), CURLOPT_POSTFIELDS, result.c_str());
        curl_easy_setopt(post_curl.get(), CURLOPT_POSTFIELDSIZE, result.size());

        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(post_curl.get(), CURLOPT_HTTPHEADER, headers);

        curl_easy_perform(post_curl.get());
        curl_slist_free_all(headers);
    }

    curl_global_cleanup();
    return 0;
}
