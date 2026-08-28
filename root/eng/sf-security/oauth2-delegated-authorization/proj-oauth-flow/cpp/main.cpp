#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <random>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <span>
#include <openssl/sha.h>
#include <openssl/rand.h>

class OAuthClient {
public:
    OAuthClient(std::string auth_server_url,
                std::string client_id,
                std::string redirect_uri,
                std::string client_secret = "",
                int clock_skew_seconds = 60)
        : auth_server_url_(std::move(auth_server_url))
        , client_id_(std::move(client_id))
        , redirect_uri_(std::move(redirect_uri))
        , client_secret_(std::move(client_secret))
        , clock_skew_seconds_(clock_skew_seconds)
    {
        authorize_endpoint_ = auth_server_url_ + "/oauth/authorize";
        token_endpoint_ = auth_server_url_ + "/oauth/token";
    }

    static std::string base64url_encode(std::span<const uint8_t> data) {
        static constexpr char tbl[] =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
        std::string out;
        out.reserve(((data.size() + 2) / 3) * 4);

        size_t i = 0;
        while (i < data.size()) {
            uint32_t octet_a = data[i++];
            uint32_t octet_b = (i < data.size()) ? data[i++] : 0;
            uint32_t octet_c = (i < data.size()) ? data[i++] : 0;

            uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

            out.push_back(tbl[(triple >> 18) & 0x3F]);
            out.push_back(tbl[(triple >> 12) & 0x3F]);
            if (i > data.size() + 1) break;
            out.push_back(tbl[(triple >> 6) & 0x3F]);
            if (i > data.size()) break;
            out.push_back(tbl[triple & 0x3F]);
        }
        return out;
    }

    std::pair<std::string, std::string> generate_pkce_pair() {
        std::vector<uint8_t> random_bytes(64);
        if (RAND_bytes(random_bytes.data(), static_cast<int>(random_bytes.size())) != 1) {
            throw std::runtime_error("CSPRNG: збій отримання випадкових байтів OpenSSL");
        }
        std::string verifier = base64url_encode(random_bytes);

        uint8_t hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const uint8_t*>(verifier.data()), verifier.size(), hash);
        std::string challenge = base64url_encode(std::span<const uint8_t>(hash, SHA256_DIGEST_LENGTH));

        return {verifier, challenge};
    }

    std::string create_authorization_url(const std::vector<std::string>& scopes) {
        auto [verifier, challenge] = generate_pkce_pair();
        
        std::vector<uint8_t> state_bytes(32);
        RAND_bytes(state_bytes.data(), static_cast<int>(state_bytes.size()));
        std::string state = base64url_encode(state_bytes);

        pending_verifier_ = verifier;
        pending_state_ = state;

        std::string scope_str;
        for (size_t i = 0; i < scopes.size(); ++i) {
            if (i > 0) scope_str += "+";
            scope_str += scopes[i];
        }

        std::ostringstream ss;
        ss << authorize_endpoint_
           << "?response_type=code"
           << "&client_id=" << client_id_
           << "&redirect_uri=" << redirect_uri_
           << "&scope=" << scope_str
           << "&state=" << state
           << "&code_challenge=" << challenge
           << "&code_challenge_method=S256";

        return ss.str();
    }

    bool validate_state(std::string_view returned_state) const noexcept {
        if (pending_state_.empty() || pending_state_.size() != returned_state.size()) {
            return false;
        }
        // Порівняння сталого часу для захисту від timing attacks
        int diff = 0;
        for (size_t i = 0; i < pending_state_.size(); ++i) {
            diff |= (pending_state_[i] ^ returned_state[i]);
        }
        return diff == 0;
    }

    bool is_token_expired() const noexcept {
        auto now = std::chrono::system_clock::now();
        auto threshold = expires_at_ - std::chrono::seconds(clock_skew_seconds_);
        return now >= threshold;
    }

    void set_tokens(std::string access, std::string refresh, int expires_in_sec) {
        access_token_ = std::move(access);
        refresh_token_ = std::move(refresh);
        expires_at_ = std::chrono::system_clock::now() + std::chrono::seconds(expires_in_sec);
    }

    const std::string& get_pending_verifier() const noexcept { return pending_verifier_; }
    const std::string& get_access_token() const noexcept { return access_token_; }
    const std::string& get_refresh_token() const noexcept { return refresh_token_; }

private:
    std::string auth_server_url_;
    std::string authorize_endpoint_;
    std::string token_endpoint_;
    std::string client_id_;
    std::string redirect_uri_;
    std::string client_secret_;
    int clock_skew_seconds_;

    std::string access_token_;
    std::string refresh_token_;
    std::chrono::system_clock::time_point expires_at_;

    std::string pending_verifier_;
    std::string pending_state_;
};
