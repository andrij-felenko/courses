/* ============================================================================
 * pkcs11_sign.c — Апаратне накладання підпису ECDSA через PKCS#11 API
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Базові заголовки PKCS#11 */
#define CK_PTR *
#define CK_DECLARE_FUNCTION(returnType, name) returnType name
#define CK_DECLARE_FUNCTION_POINTER(returnType, name) returnType (* name)
#define CK_CALLBACK_FUNCTION(returnType, name) returnType (* name)
#ifndef NULL_PTR
#define NULL_PTR NULL
#endif

/* Визначення базових типів PKCS#11 для компіляції без зовнішніх залежностей */
typedef unsigned char     CK_BYTE;
typedef unsigned char     CK_BBOOL;
typedef unsigned long int CK_ULONG;
typedef CK_ULONG          CK_RV;
typedef CK_ULONG          CK_SLOT_ID;
typedef CK_SESSION_HANDLE CK_SESSION_HANDLE;
typedef CK_OBJECT_HANDLE  CK_OBJECT_HANDLE;
typedef CK_OBJECT_CLASS   CK_OBJECT_CLASS;
typedef CK_KEY_TYPE       CK_KEY_TYPE;
typedef CK_MECHANISM_TYPE CK_MECHANISM_TYPE;
typedef CK_ATTRIBUTE_TYPE CK_ATTRIBUTE_TYPE;
typedef CK_USER_TYPE      CK_USER_TYPE;
typedef CK_BYTE          *CK_BYTE_PTR;
typedef CK_ULONG         *CK_ULONG_PTR;
typedef CK_SLOT_ID       *CK_SLOT_ID_PTR;
typedef CK_SESSION_HANDLE*CK_SESSION_HANDLE_PTR;
typedef CK_OBJECT_HANDLE *CK_OBJECT_HANDLE_PTR;
typedef CK_BYTE          *CK_UTF8CHAR_PTR;

#define CK_TRUE  1
#define CK_FALSE 0

#define CKR_OK                       0x00000000UL
#define CKR_BUFFER_TOO_SMALL         0x00000150UL
#define CKS_RO_USER_FUNCTIONS        0x00000002UL
#define CKF_SERIAL_SESSION           0x00000004UL
#define CKU_USER                     0x00000001UL

#define CKO_PRIVATE_KEY              0x00000003UL
#define CKK_EC                       0x00000003UL
#define CKM_ECDSA                    0x00001041UL

#define CKA_CLASS                    0x00000000UL
#define CKA_TOKEN                    0x00000001UL
#define CKA_PRIVATE                  0x00000002UL
#define CKA_LABEL                    0x00000003UL
#define CKA_KEY_TYPE                 0x00000100UL
#define CKA_SIGN                     0x00000108UL
#define CKA_EXTRACTABLE              0x00000162UL

typedef struct CK_ATTRIBUTE {
    CK_ATTRIBUTE_TYPE type;
    void             *pValue;
    CK_ULONG          ulValueLen;
} CK_ATTRIBUTE;
typedef CK_ATTRIBUTE *CK_ATTRIBUTE_PTR;

typedef struct CK_MECHANISM {
    CK_MECHANISM_TYPE mechanism;
    void             *pParameter;
    CK_ULONG          ulParameterLen;
} CK_MECHANISM;
typedef CK_MECHANISM *CK_MECHANISM_PTR;

/* Структура списку функцій Cryptoki */
typedef struct CK_FUNCTION_LIST CK_FUNCTION_LIST;
typedef CK_FUNCTION_LIST *CK_FUNCTION_LIST_PTR;
typedef CK_FUNCTION_LIST_PTR *CK_FUNCTION_LIST_PTR_PTR;

struct CK_FUNCTION_LIST {
    void *version;
    CK_RV (*C_Initialize)(void *pInitArgs);
    CK_RV (*C_Finalize)(void *pReserved);
    CK_RV (*C_GetFunctionList)(CK_FUNCTION_LIST_PTR_PTR ppFunctionList);
    CK_RV (*C_GetSlotList)(CK_BBOOL tokenPresent, CK_SLOT_ID_PTR pSlotList, CK_ULONG_PTR pulCount);
    CK_RV (*C_OpenSession)(CK_SLOT_ID slotID, CK_ULONG flags, void *pApp, void *Notify, CK_SESSION_HANDLE_PTR phSession);
    CK_RV (*C_CloseSession)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_Login)(CK_SESSION_HANDLE hSession, CK_USER_TYPE userType, CK_UTF8CHAR_PTR pPin, CK_ULONG ulPinLen);
    CK_RV (*C_Logout)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_FindObjectsInit)(CK_SESSION_HANDLE hSession, CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount);
    CK_RV (*C_FindObjects)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE_PTR phObject, CK_ULONG ulMax, CK_ULONG_PTR pulCount);
    CK_RV (*C_FindObjectsFinal)(CK_SESSION_HANDLE hSession);
    CK_RV (*C_GetAttributeValue)(CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hObject, CK_ATTRIBUTE_PTR pTemplate, CK_ULONG ulCount);
    CK_RV (*C_SignInit)(CK_SESSION_HANDLE hSession, CK_MECHANISM_PTR pMech, CK_OBJECT_HANDLE hKey);
    CK_RV (*C_Sign)(CK_SESSION_HANDLE hSession, CK_BYTE_PTR pData, CK_ULONG ulDataLen, CK_BYTE_PTR pSignature, CK_ULONG_PTR pulSignatureLen);
};

/* Допоміжна функція пошуку приватного ключа за назвою мітки */
static CK_OBJECT_HANDLE find_private_key(CK_FUNCTION_LIST_PTR pF, CK_SESSION_HANDLE hSession, const char *label) {
    CK_OBJECT_CLASS keyClass = CKO_PRIVATE_KEY;
    CK_BBOOL bTrue = CK_TRUE;
    
    CK_ATTRIBUTE searchTemplate[] = {
        { CKA_CLASS,   &keyClass, sizeof(keyClass) },
        { CKA_SIGN,    &bTrue,    sizeof(bTrue) },
        { CKA_LABEL,   (void *)label, (CK_ULONG)strlen(label) }
    };

    CK_RV rv = pF->C_FindObjectsInit(hSession, searchTemplate, 3);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка C_FindObjectsInit: 0x%08lX\n", rv);
        return 0;
    }

    CK_OBJECT_HANDLE hObject = 0;
    CK_ULONG objectCount = 0;
    rv = pF->C_FindObjects(hSession, &hObject, 1, &objectCount);
    pF->C_FindObjectsFinal(hSession);

    if (rv != CKR_OK || objectCount == 0) {
        fprintf(stderr, "[!] Приватний ключ із міткою '%s' не знайдено в токені.\n", label);
        return 0;
    }

    return hObject;
}

/* Перевірка чи ключ дійсно є невитягуваним (CKA_EXTRACTABLE == FALSE) */
static bool verify_non_extractable(CK_FUNCTION_LIST_PTR pF, CK_SESSION_HANDLE hSession, CK_OBJECT_HANDLE hKey) {
    CK_BBOOL isExtractable = CK_TRUE;
    CK_ATTRIBUTE attrTemplate[] = {
        { CKA_EXTRACTABLE, &isExtractable, sizeof(isExtractable) }
    };

    CK_RV rv = pF->C_GetAttributeValue(hSession, hKey, attrTemplate, 1);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Не вдалося перевірити атрибут CKA_EXTRACTABLE: 0x%08lX\n", rv);
        return false;
    }

    if (isExtractable == CK_TRUE) {
        fprintf(stderr, "[УВАГА] Ключ позначено як витягуваний (CKA_EXTRACTABLE = TRUE)!\n");
        return false;
    }

    printf("[+] Апаратна перевірка: Ключ суворо невитягуваний (CKA_EXTRACTABLE = FALSE).\n");
    return true;
}

/* Головна функція виконання апаратного підпису */
int perform_hardware_sign(CK_FUNCTION_LIST_PTR pF, const char *pin, const char *keyLabel,
                          const unsigned char *digest32, unsigned char *outSig, size_t *outSigLen) {
    CK_RV rv = pF->C_Initialize(NULL_PTR);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] C_Initialize зазнав невдачі: 0x%08lX\n", rv);
        return -1;
    }

    /* 1. Пошук підключених слотів із токенами */
    CK_ULONG slotCount = 0;
    rv = pF->C_GetSlotList(CK_TRUE, NULL_PTR, &slotCount);
    if (rv != CKR_OK || slotCount == 0) {
        fprintf(stderr, "[!] Жодного апаратного токена не підключено до системи.\n");
        pF->C_Finalize(NULL_PTR);
        return -2;
    }

    CK_SLOT_ID *slots = (CK_SLOT_ID *)malloc(slotCount * sizeof(CK_SLOT_ID));
    pF->C_GetSlotList(CK_TRUE, slots, &slotCount);
    CK_SLOT_ID targetSlot = slots[0];
    free(slots);

    /* 2. Відкриття сесії */
    CK_SESSION_HANDLE hSession = 0;
    rv = pF->C_OpenSession(targetSlot, CKF_SERIAL_SESSION, NULL_PTR, NULL_PTR, &hSession);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка відкриття сесії C_OpenSession: 0x%08lX\n", rv);
        pF->C_Finalize(NULL_PTR);
        return -3;
    }

    /* 3. Автентифікація користувача через PIN-код */
    rv = pF->C_Login(hSession, CKU_USER, (CK_UTF8CHAR_PTR)pin, (CK_ULONG)strlen(pin));
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка входу C_Login (невірний PIN?): 0x%08lX\n", rv);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -4;
    }

    /* 4. Пошук приватного ключа */
    CK_OBJECT_HANDLE hKey = find_private_key(pF, hSession, keyLabel);
    if (hKey == 0) {
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -5;
    }

    verify_non_extractable(pF, hSession, hKey);

    /* 5. Накладання цифрового підпису ECDSA всередині чипа */
    CK_MECHANISM signMech = { CKM_ECDSA, NULL_PTR, 0 };
    rv = pF->C_SignInit(hSession, &signMech, hKey);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка ініціалізації C_SignInit: 0x%08lX\n", rv);
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -6;
    }

    CK_ULONG sigLen = (CK_ULONG)(*outSigLen);
    rv = pF->C_Sign(hSession, (CK_BYTE_PTR)digest32, 32, (CK_BYTE_PTR)outSig, &sigLen);
    if (rv != CKR_OK) {
        fprintf(stderr, "[!] Помилка накладання підпису C_Sign: 0x%08lX\n", rv);
        pF->C_Logout(hSession);
        pF->C_CloseSession(hSession);
        pF->C_Finalize(NULL_PTR);
        return -7;
    }

    *outSigLen = (size_t)sigLen;
    printf("[+] Цифровий підпис успішно накладено в апаратному модулі (%lu байтів).\n", sigLen);

    /* 6. Очищення ресурсів */
    pF->C_Logout(hSession);
    pF->C_CloseSession(hSession);
    pF->C_Finalize(NULL_PTR);
    return 0;
}
