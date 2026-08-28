#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <array>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <openssl/sha.h>

namespace pip_client {

// Нормалізація імені проекту за стандартом PEP 503 з нульовим виділенням динамічної пам'яті
std::string normalize_project_name(std::string_view name) {
    std::string result;
    result.reserve(name.size());
    bool last_was_dash = false;

    for (char ch : name) {
        if (ch == '-' || ch == '_' || ch == '.') {
            if (!last_was_dash && !result.empty()) {
                result.push_back('-');
                last_was_dash = true;
            }
        } else {
            result.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(ch))));
            last_was_dash = false;
        }
    }
    if (!result.empty() && result.back() == '-') {
        result.pop_back();
    }
    return result;
}

// RAII-обгортка над криптографічним контекстом OpenSSL SHA256
class Sha256StreamVerifier {
public:
    Sha256StreamVerifier() {
        SHA256_Init(&ctx_);
    }

    void update(const char* data, std::size_t length) {
        SHA256_Update(&ctx_, data, length);
    }

    std::string finalize() {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> digest{};
        SHA256_Final(digest.data(), &ctx_);

        std::ostringstream oss;
        for (unsigned char byte : digest) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        return oss.str();
    }

private:
    SHA256_CTX ctx_;
};

// Потокова перевірка цілісності вхідного бінарного потоку std::istream
bool verify_stream_integrity(std::istream& stream, std::string_view expected_sha256) {
    Sha256StreamVerifier verifier;
    std::vector<char> buffer(65536);

    while (stream.read(buffer.data(), static_cast<std::streamsize>(buffer.size())) || stream.gcount() > 0) {
        verifier.update(buffer.data(), static_cast<std::size_t>(stream.gcount()));
    }

    std::string computed = verifier.finalize();
    return (computed == expected_sha256);
}

} // namespace pip_client
