#include <stdio.h>
#include <string.h>

/* Типізовані структури PKCS#11 (Cryptoki) */
typedef unsigned long CK_RV;
typedef unsigned long CK_SESSION_HANDLE;
typedef unsigned long CK_OBJECT_HANDLE;
typedef unsigned long CK_MECHANISM_TYPE;

#define CKR_OK 0x00000000
#define CKM_SHA256_HMAC 0x00000251

typedef struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void *pParameter;
    unsigned long ulParameterLen;
} CK_MECHANISM;

/* Сигнатури стандартних функцій Cryptoki */
CK_RV C_SignInit(CK_SESSION_HANDLE hSession, CK_MECHANISM *pMechanism, CK_OBJECT_HANDLE hKey);
CK_RV C_Sign(CK_SESSION_HANDLE hSession, unsigned char *pData, unsigned long ulDataLen,
             unsigned char *pSignature, unsigned long *pulSignatureLen);

/* Приклад використання апаратного HMAC */
int hsm_sign_message(CK_SESSION_HANDLE session, CK_OBJECT_HANDLE hmac_key,
                     const unsigned char *data, unsigned long data_len,
                     unsigned char *signature, unsigned long *sig_len)
{
    CK_MECHANISM mech = { CKM_SHA256_HMAC, NULL, 0 };
    CK_RV rv;

    /* 1. Ініціалізація операції підпису на захищеному токені */
    rv = C_SignInit(session, &mech, hmac_key);
    if (rv != CKR_OK) return 0;

    /* 2. Обчислення підпису всередині HSM (ключ не потрапляє в RAM хоста) */
    rv = C_Sign(session, (unsigned char *)data, data_len, signature, sig_len);
    return (rv == CKR_OK);
}
