// ============================================================================
// pkcs11_sign.cpp — Ідіоматична обгортка C++20 з RAII для PKCS#11
// ============================================================================
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <stdexcept>
#include <format>
#include <cstdint>

// Оголошення типів PKCS#11
using CK_BYTE = unsigned char;
using CK_BBOOL = unsigned char;
using CK_ULONG = unsigned long int;
using CK_RV = CK_ULONG;
using CK_SLOT_ID = CK_ULONG;
using CK_SESSION_HANDLE = CK_ULONG;
using CK_OBJECT_HANDLE = CK_ULONG;
using CK_ATTRIBUTE_TYPE = CK_ULONG;
using CK_MECHANISM_TYPE = CK_ULONG;
using CK_USER_TYPE = CK_ULONG;

constexpr CK_BBOOL CK_TRUE = 1;
constexpr CK_BBOOL CK_FALSE = 0;
constexpr CK_RV CKR_OK = 0x00000000UL;
constexpr CK_ULONG CKF_SERIAL_SESSION = 0x00000004UL;
constexpr CK_USER_TYPE CKU_USER = 0x00000001UL;
constexpr CK_ULONG CKO_PRIVATE_KEY = 0x00000003UL;
constexpr CK_MECHANISM_TYPE CKM_ECDSA = 0x00001041UL;

constexpr CK_ATTRIBUTE_TYPE CKA_CLASS = 0x00000000UL;
constexpr CK_ATTRIBUTE_TYPE CKA_LABEL = 0x00000003UL;
constexpr CK_ATTRIBUTE_TYPE CKA_SIGN = 0x00000108UL;
constexpr CK_ATTRIBUTE_TYPE CKA_EXTRACTABLE = 0x00000162UL;

struct CK_ATTRIBUTE {
    CK_ATTRIBUTE_TYPE type;
    void* pValue;
    CK_ULONG ulValueLen;
};

struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void* pParameter;
    CK_ULONG ulParameterLen;
};

struct CK_FUNCTION_LIST {
    void* version;
    CK_RV (*C_Initialize)(void* pInitArgs);
    CK_RV (*C_Finalize)(void* pReserved);
    CK_RV (*C_GetFunctionList)(CK_FUNCTION_LIST** ppFunctionList);
    CK_RV (*C_GetSlotList)(CK_BBOOL tokenPresent, CK_SLOT_ID* pSlotList, CK_ULONG* pulCount);
    CK_RV (*C_OpenSession)(CK_SLOT_ID slotID, CK_ULONG flags, void* pApp, void* Notify, CK_SESSION_HANDLE* phSession);
    CK_RV (*C_CloseSession)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_Login)(CK_SESSION_HANDLE hSession, CK_USER_TYPE userType, CK_BYTE* pPin, CK_ULONG ulPinLen);
    CK_RV (*C_Logout)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_FindObjectsInit)(CK_SESSION_HANDLE hSession, CK_ATTRIBUTE* pTemplate, CK_ULONG ulCount);
    CK_RV (*C_FindObjects)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE* phObject, CK_ULONG ulMax, CK_ULONG* pulCount);
    CK_RV (*C_FindObjectsFinal)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_GetAttributeValue)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hObject, CK_ATTRIBUTE* pTemplate, CK_ULONG ulCount);
    CK_RV (*C_SignInit)(CK_SESSION_HANDLE hSession, CK_MECHANISM* pMech, CK_OBJECT_HANDLE hKey);
    CK_RV (*C_Sign)(CK_SESSION_HANDLE hSession, CK_BYTE* pData, CK_ULONG ulDataLen, CK_BYTE* pSignature, CK_ULONG* pulSignatureLen);
};

namespace pkcs11 {

// Виняток безпеки PKCS#11
class CryptokiException : public std::runtime_error {
public:
    explicit CryptokiException(std::string_view operation, CK_RV errorCode)
        : std::runtime_error(std::format("{} failed with code: 0x{:08X}", operation, errorCode)),
          code_(errorCode) {}

    [[nodiscard]] CK_RV error_code() const noexcept { return code_; }
private:
    CK_RV code_;
};

// RAII обгортка для управління глобальним станом бібліотеки PKCS#11
class LibraryContext {
public:
    explicit LibraryContext(CK_FUNCTION_LIST* functionList) : f_(functionList) {
        if (!f_) throw std::invalid_argument("Function list cannot be null");
        if (auto rv = f_->C_Initialize(nullptr); rv != CKR_OK) {
            throw CryptokiException("C_Initialize", rv);
        }
    }

    ~LibraryContext() noexcept {
        f_->C_Finalize(nullptr);
    }

    LibraryContext(const LibraryContext&) = delete;
    LibraryContext& operator=(const LibraryContext&) = delete;

    [[nodiscard]] CK_FUNCTION_LIST* functions() const noexcept { return f_; }

private:
    CK_FUNCTION_LIST* f_{nullptr};
};

// RAII обгортка активної сесії токена з автоматичним входом/виходом
class TokenSession {
public:
    TokenSession(LibraryContext& ctx, CK_SLOT_ID slotId, std::string_view pin)
        : ctx_(ctx) {
        auto* f = ctx_.functions();
        if (auto rv = f->C_OpenSession(slotId, CKF_SERIAL_SESSION, nullptr, nullptr, &session_); rv != CKR_OK) {
            throw CryptokiException("C_OpenSession", rv);
        }

        if (auto rv = f->C_Login(session_, CKU_USER,
                                reinterpret_cast<CK_BYTE*>(const_cast<char*>(pin.data())),
                                static_cast<CK_ULONG>(pin.size())); rv != CKR_OK) {
            f->C_CloseSession(session_);
            throw CryptokiException("C_Login", rv);
        }
        isLoggedIn_ = true;
    }

    ~TokenSession() noexcept {
        auto* f = ctx_.functions();
        if (isLoggedIn_) {
            f->C_Logout(session_);
        }
        if (session_ != 0) {
            f->C_CloseSession(session_);
        }
    }

    TokenSession(const TokenSession&) = delete;
    TokenSession& operator=(const TokenSession&) = delete;

    // Пошук дескриптора приватного ключа
    [[nodiscard]] CK_OBJECT_HANDLE findPrivateKey(std::string_view label) const {
        auto* f = ctx_.functions();
        CK_OBJECT_CLASS keyClass = CKO_PRIVATE_KEY;
        CK_BBOOL bTrue = CK_TRUE;

        std::vector<CK_ATTRIBUTE> criteria = {
            { CKA_CLASS, &keyClass, sizeof(keyClass) },
            { CKA_SIGN,  &bTrue,    sizeof(bTrue) },
            { CKA_LABEL, const_cast<char*>(label.data()), static_cast<CK_ULONG>(label.size()) }
        };

        if (auto rv = f->C_FindObjectsInit(session_, criteria.data(), static_cast<CK_ULONG>(criteria.size())); rv != CKR_OK) {
            throw CryptokiException("C_FindObjectsInit", rv);
        }

        CK_OBJECT_HANDLE hKey = 0;
        CK_ULONG count = 0;
        auto rvFind = f->C_FindObjects(session_, &hKey, 1, &count);
        f->C_FindObjectsFinal(session_);

        if (rvFind != CKR_OK) throw CryptokiException("C_FindObjects", rvFind);
        if (count == 0) throw std::runtime_error(std::format("Private key '{}' not found in token", label));

        return hKey;
    }

    // Перевірка невитягуваності ключа
    [[nodiscard]] bool isKeyNonExtractable(CK_OBJECT_HANDLE hKey) const {
        CK_BBOOL extractable = CK_TRUE;
        CK_ATTRIBUTE attr = { CKA_EXTRACTABLE, &extractable, sizeof(extractable) };
        if (auto rv = ctx_.functions()->C_GetAttributeValue(session_, hKey, &attr, 1); rv != CKR_OK) {
            throw CryptokiException("C_GetAttributeValue", rv);
        }
        return extractable == CK_FALSE;
    }

    // Накладання апаратного підпису ECDSA на 32-байтний дайджест
    [[nodiscard]] std::vector<uint8_t> signDigest(CK_OBJECT_HANDLE hKey, std::span<const uint8_t, 32> digest) const {
        auto* f = ctx_.functions();
        CK_MECHANISM mech = { CKM_ECDSA, nullptr, 0 };

        if (auto rv = f->C_SignInit(session_, &mech, hKey); rv != CKR_OK) {
            throw CryptokiException("C_SignInit", rv);
        }

        // Запит розміру вихідного підпису
        CK_ULONG sigLen = 0;
        if (auto rv = f->C_Sign(session_, const_cast<CK_BYTE*>(digest.data()), 32, nullptr, &sigLen); rv != CKR_OK) {
            throw CryptokiException("C_Sign (size query)", rv);
        }

        std::vector<uint8_t> signature(sigLen);
        if (auto rv = f->C_Sign(session_, const_cast<CK_BYTE*>(digest.data()), 32, signature.data(), &sigLen); rv != CKR_OK) {
            throw CryptokiException("C_Sign (signature execution)", rv);
        }
        signature.resize(sigLen);
        return signature;
    }

private:
    LibraryContext& ctx_;
    CK_SESSION_HANDLE session_{0};
    bool isLoggedIn_{false};
};

} // namespace pkcs11
