#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <expected>
#include <chrono>
#include <curl/curl.h>

/* RAII-обгортка над дескриптором CURL для автоматичного звільнення ресурсу */
class CurlSession {
public:
    CurlSession() : handle_(curl_easy_init(), curl_easy_cleanup) {}

    [[nodiscard]] CURL* get() const noexcept { return handle_.get(); }
    [[nodiscard]] bool isValid() const noexcept { return handle_ != nullptr; }

private:
    std::unique_ptr<CURL, decltype(&curl_easy_cleanup)> handle_;
};

/* Клієнт взаємодії з точкою ухвалення рішень OPA (PDP) */
class OpaClient {
public:
    explicit OpaClient(std::string endpoint) : endpoint_(std::move(endpoint)) {}

    [[nodiscard]] std::expected<bool, std::string> evaluate(std::string_view jsonInput) const {
        CurlSession session;
        if (!session.isValid()) {
            return std::unexpected("Не вдалося ініціалізувати CURL сесію");
        }

        std::string responseBody;
        struct curl_slist* rawHeaders = nullptr;
        rawHeaders = curl_slist_append(rawHeaders, "Content-Type: application/json");
        std::unique_ptr<curl_slist, decltype(&curl_slist_free_all)> headers(rawHeaders, curl_slist_free_all);

        // Формуємо обгортку кореневого об'єкта {"input": ...}
        std::string wrappedPayload = "{\"input\":" + std::string(jsonInput) + "}";

        auto writeCallback = [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
            auto* target = static_cast<std::string*>(userdata);
            const size_t totalBytes = size * nmemb;
            target->append(ptr, totalBytes);
            return totalBytes;
        };

        curl_easy_setopt(session.get(), CURLOPT_URL, endpoint_.c_str());
        curl_easy_setopt(session.get(), CURLOPT_POSTFIELDS, wrappedPayload.c_str());
        curl_easy_setopt(session.get(), CURLOPT_HTTPHEADER, headers.get());
        curl_easy_setopt(session.get(), CURLOPT_WRITEFUNCTION, +writeCallback);
        curl_easy_setopt(session.get(), CURLOPT_WRITEDATA, &responseBody);
        curl_easy_setopt(session.get(), CURLOPT_TIMEOUT_MS, 500L);
        curl_easy_setopt(session.get(), CURLOPT_NOSIGNAL, 1L);

        const CURLcode code = curl_easy_perform(session.get());
        if (code != CURLE_OK) {
            return std::unexpected(std::string("Мережевий збій запиту до PDP: ") + curl_easy_strerror(code));
        }

        long httpCode = 0;
        curl_easy_getinfo(session.get(), CURLINFO_RESPONSE_CODE, &httpCode);
        if (httpCode != 200) {
            return std::unexpected("PDP повернув статус помилки HTTP: " + std::to_string(httpCode));
        }

        // Перевіряємо наявність булевого результату у відповіді
        const bool isAllowed = (responseBody.find("\"result\":true") != std::string::npos);
        return isAllowed;
    }

private:
    std::string endpoint_;
};

int main() {
    const OpaClient client("http://localhost:8181/v1/data/authz/allow");
    const std::string_view userPayload = R"({"user":{"role":"admin","mfa":true},"method":"POST"})";

    auto result = client.evaluate(userPayload);
    if (!result) {
        std::cerr << "Помилка комунікації з OPA: " << result.error() << '\n';
        return 1;
    }

    if (*result) {
        std::cout << "C++ Client: Доступ дозволено OPA PDP (200 OK)\n";
    } else {
        std::cout << "C++ Client: Доступ відхилено OPA PDP (403 Forbidden)\n";
    }

    return 0;
}
