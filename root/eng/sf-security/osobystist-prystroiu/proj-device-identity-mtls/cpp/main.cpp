#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <cstring>

#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/x509_crt.h"
#include "mbedtls/pk.h"
#include "mbedtls/error.h"

namespace device_security {

enum class ErrorCode {
    SiliconUidReadFailed,
    DrbgInitFailed,
    CertificateParseFailed,
    ConfigDefaultsFailed,
    SslSetupFailed,
    HostnameSetFailed,
    NetworkConnectFailed,
    HandshakeFailed,
    HardwareSigningFailed
};

enum class KeySlot : uint8_t {
    IDevID = 0x00,
    LDevID = 0x01
};

/* RAII-обгортка апаратного модуля безпеки */
class HardwareSecurityModule {
public:
    HardwareSecurityModule() : active_slot_(KeySlot::IDevID) {
        /* Зчитування 128-бітного апаратного серійника */
        const std::array<uint8_t, 16> mock_uid = {
            0x53, 0x54, 0x4D, 0x33, 0x32, 0x48, 0x35, 0x30,
            0xAA, 0xBB, 0xCC, 0xDD, 0x01, 0x02, 0x03, 0x04
        };
        uid_ = mock_uid;
    }

    [[nodiscard]] std::span<const uint8_t> uid() const noexcept {
        return uid_;
    }

    void select_key_slot(KeySlot slot) noexcept {
        active_slot_ = slot;
    }

    [[nodiscard]] std::expected<std::pair<std::array<uint8_t, 32>, std::array<uint8_t, 32>>, ErrorCode>
    sign_digest(std::span<const uint8_t> hash) const noexcept {
        if (hash.size() != 32) {
            return std::unexpected(ErrorCode::HardwareSigningFailed);
        }
        std::array<uint8_t, 32> r{}, s{};
        r.fill(0xA5);
        s.fill(0x5A);
        return std::make_pair(r, s);
    }

private:
    std::array<uint8_t, 16> uid_{};
    KeySlot active_slot_;
};

/* RAII-керування ресурсами mbedTLS */
struct MbedTlsDeleters {
    void operator()(mbedtls_net_context* p)      const noexcept { mbedtls_net_free(p); delete p; }
    void operator()(mbedtls_ssl_context* p)      const noexcept { mbedtls_ssl_free(p); delete p; }
    void operator()(mbedtls_ssl_config* p)       const noexcept { mbedtls_ssl_config_free(p); delete p; }
    void operator()(mbedtls_x509_crt* p)         const noexcept { mbedtls_x509_crt_free(p); delete p; }
    void operator()(mbedtls_pk_context* p)       const noexcept { mbedtls_pk_free(p); delete p; }
    void operator()(mbedtls_entropy_context* p)  const noexcept { mbedtls_entropy_free(p); delete p; }
    void operator()(mbedtls_ctr_drbg_context* p) const noexcept { mbedtls_ctr_drbg_free(p); delete p; }
};

/* Клієнт mTLS з апаратною автентифікацією */
class DeviceMtlsClient {
public:
    explicit DeviceMtlsClient(std::shared_ptr<HardwareSecurityModule> hsm)
        : hsm_(std::move(hsm)),
          net_(new mbedtls_net_context),
          ssl_(new mbedtls_ssl_context),
          conf_(new mbedtls_ssl_config),
          cacert_(new mbedtls_x509_crt),
          clicert_(new mbedtls_x509_crt),
          pkey_(new mbedtls_pk_context),
          entropy_(new mbedtls_entropy_context),
          drbg_(new mbedtls_ctr_drbg_context) {
        
        mbedtls_net_init(net_.get());
        mbedtls_ssl_init(ssl_.get());
        mbedtls_ssl_config_init(conf_.get());
        mbedtls_x509_crt_init(cacert_.get());
        mbedtls_x509_crt_init(clicert_.get());
        mbedtls_pk_init(pkey_.get());
        mbedtls_entropy_init(entropy_.get());
        mbedtls_ctr_drbg_init(drbg_.get());
    }

    [[nodiscard]] std::expected<void, ErrorCode>
    connect(std::string_view host, std::string_view port,
            std::string_view ca_pem, std::string_view dev_cert_pem) {
        
        constexpr std::string_view pers = "device_identity_mtls_cpp";
        if (mbedtls_ctr_drbg_seed(drbg_.get(), mbedtls_entropy_func, entropy_.get(),
                                  reinterpret_cast<const unsigned char*>(pers.data()),
                                  pers.size()) != 0) {
            return std::unexpected(ErrorCode::DrbgInitFailed);
        }

        if (mbedtls_x509_crt_parse(cacert_.get(),
                                   reinterpret_cast<const unsigned char*>(ca_pem.data()),
                                   ca_pem.size() + 1) != 0 ||
            mbedtls_x509_crt_parse(clicert_.get(),
                                   reinterpret_cast<const unsigned char*>(dev_cert_pem.data()),
                                   dev_cert_pem.size() + 1) != 0) {
            return std::unexpected(ErrorCode::CertificateParseFailed);
        }

        /* Прив'язка апаратного HSM до контексту відкритого ключа */
        pkey_->pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
        pkey_->pk_ctx  = hsm_.get();

        if (mbedtls_ssl_config_defaults(conf_.get(), MBEDTLS_SSL_IS_CLIENT,
                                        MBEDTLS_SSL_TRANSPORT_STREAM,
                                        MBEDTLS_SSL_PRESET_DEFAULT) != 0) {
            return std::unexpected(ErrorCode::ConfigDefaultsFailed);
        }

        mbedtls_ssl_conf_authmode(conf_.get(), MBEDTLS_SSL_VERIFY_REQUIRED);
        mbedtls_ssl_conf_ca_chain(conf_.get(), cacert_.get(), nullptr);
        mbedtls_ssl_conf_own_cert(conf_.get(), clicert_.get(), pkey_.get());
        mbedtls_ssl_conf_rng(conf_.get(), mbedtls_ctr_drbg_random, drbg_.get());

        if (mbedtls_ssl_setup(ssl_.get(), conf_.get()) != 0) {
            return std::unexpected(ErrorCode::SslSetupFailed);
        }

        if (mbedtls_ssl_set_hostname(ssl_.get(), std::string(host).c_str()) != 0) {
            return std::unexpected(ErrorCode::HostnameSetFailed);
        }

        if (mbedtls_net_connect(net_.get(), std::string(host).c_str(),
                                std::string(port).c_str(), MBEDTLS_NET_PROTO_TCP) != 0) {
            return std::unexpected(ErrorCode::NetworkConnectFailed);
        }

        mbedtls_ssl_set_bio(ssl_.get(), net_.get(), mbedtls_net_send, mbedtls_net_recv, nullptr);

        int ret = 0;
        while ((ret = mbedtls_ssl_handshake(ssl_.get())) != 0) {
            if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
                return std::unexpected(ErrorCode::HandshakeFailed);
            }
        }

        return {};
    }

private:
    std::shared_ptr<HardwareSecurityModule> hsm_;
    std::unique_ptr<mbedtls_net_context, MbedTlsDeleters>      net_;
    std::unique_ptr<mbedtls_ssl_context, MbedTlsDeleters>      ssl_;
    std::unique_ptr<mbedtls_ssl_config, MbedTlsDeleters>       conf_;
    std::unique_ptr<mbedtls_x509_crt, MbedTlsDeleters>         cacert_;
    std::unique_ptr<mbedtls_x509_crt, MbedTlsDeleters>         clicert_;
    std::unique_ptr<mbedtls_pk_context, MbedTlsDeleters>       pkey_;
    std::unique_ptr<mbedtls_entropy_context, MbedTlsDeleters>  entropy_;
    std::unique_ptr<mbedtls_ctr_drbg_context, MbedTlsDeleters> drbg_;
};

} // namespace device_security
