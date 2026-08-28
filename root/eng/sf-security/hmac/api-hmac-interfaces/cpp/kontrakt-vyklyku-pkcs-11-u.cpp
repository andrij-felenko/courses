#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>

namespace hsm {

using SessionHandle = unsigned long;
using ObjectHandle = unsigned long;
using ReturnValue = unsigned long;

constexpr ReturnValue CkrOk = 0;
constexpr unsigned long CkmSha256Hmac = 0x00000251;

struct Mechanism {
    unsigned long mechanism;
    void* parameter;
    unsigned long parameter_len;
};

extern "C" {
    ReturnValue C_SignInit(SessionHandle hSession, Mechanism* pMechanism, ObjectHandle hKey);
    ReturnValue C_Sign(SessionHandle hSession, unsigned char* pData, unsigned long ulDataLen,
                       unsigned char* pSignature, unsigned long* pulSignatureLen);
}

class HsmHmacSigner {
public:
    HsmHmacSigner(SessionHandle session, ObjectHandle key) noexcept
        : session_(session), key_(key) {}

    [[nodiscard]] std::array<uint8_t, 32> sign(std::span<const uint8_t> data) const {
        Mechanism mech{ CkmSha256Hmac, nullptr, 0 };
        if (C_SignInit(session_, &mech, key_) != CkrOk) {
            throw std::runtime_error("Помилка C_SignInit у HSM");
        }

        std::array<uint8_t, 32> signature{};
        unsigned long sig_len = signature.size();
        if (C_Sign(session_, const_cast<unsigned char*>(data.data()), data.size(),
                   signature.data(), &sig_len) != CkrOk) {
            throw std::runtime_error("Помилка C_Sign у HSM");
        }
        return signature;
    }

private:
    SessionHandle session_;
    ObjectHandle key_;
};

} // namespace hsm
