// Ідіоматичний RAII-обгортка PAM мовою C++20
#include <iostream>
#include <memory>
#include <string>
#include <cstring>
#include <expected>
#include <vector>
#include <utility>
#include <security/pam_appl.h>

class PamSession {
public:
    static std::expected<PamSession, int> create(const std::string& service, const std::string& user, const struct pam_conv* conv) {
        pam_handle_t* handle = nullptr;
        int rc = pam_start(service.c_str(), user.c_str(), conv, &handle);
        if (rc != PAM_SUCCESS) return std::unexpected(rc);
        return PamSession(handle);
    }

    ~PamSession() {
        if (handle_) {
            pam_end(handle_, last_status_);
        }
    }

    PamSession(const PamSession&) = delete;
    PamSession& operator=(const PamSession&) = delete;
    PamSession(PamSession&& other) noexcept : handle_(std::exchange(other.handle_, nullptr)), last_status_(other.last_status_) {}

    int authenticate(int flags = 0) {
        last_status_ = pam_authenticate(handle_, flags);
        return last_status_;
    }

    int check_account(int flags = 0) {
        last_status_ = pam_acct_mgmt(handle_, flags);
        return last_status_;
    }

private:
    explicit PamSession(pam_handle_t* handle) : handle_(handle), last_status_(PAM_SUCCESS) {}
    pam_handle_t* handle_{nullptr};
    int last_status_{PAM_SUCCESS};
};

static int cpp_conv(int num_msg, const struct pam_message **msg,
                    struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0) return PAM_CONV_ERR;
    auto* reply = static_cast<struct pam_response*>(calloc(num_msg, sizeof(struct pam_response)));
    if (!reply) return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        if (msg[i]->msg_style == PAM_PROMPT_ECHO_OFF) {
            std::cout << msg[i]->msg;
            std::string pass;
            std::cin >> pass;
            reply[i].resp = strdup(pass.c_str());
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

std::expected<void, int> verify_credentials(const std::string& username) {
    struct pam_conv conv = { cpp_conv, nullptr };
    auto session = PamSession::create("check_service", username, &conv);
    if (!session) return std::unexpected(session.error());

    if (int rc = session->authenticate(); rc != PAM_SUCCESS) return std::unexpected(rc);
    if (int rc = session->check_account(); rc != PAM_SUCCESS) return std::unexpected(rc);

    return {};
}
