/* tpm2_seal_lab.c — Приклад Sealing/Unsealing мовою C з очищенням ресурсів */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tctildr.h>

#define CHECK_RC(rc, msg) \
    do { \
        if ((rc) != TSS2_RC_SUCCESS) { \
            fprintf(stderr, "[ПОМИЛКА] %s: 0x%08x\n", (msg), (rc)); \
            goto cleanup; \
        } \
    } while (0)

int main(void) {
    TSS2_RC rc = TSS2_RC_SUCCESS;
    TSS2_TCTI_CONTEXT *tcti_ctx = NULL;
    ESYS_CONTEXT *esys_ctx = NULL;
    ESYS_TR primary_handle = ESYS_TR_NONE;
    ESYS_TR session_handle = ESYS_TR_NONE;
    ESYS_TR loaded_key_handle = ESYS_TR_NONE;

    TPM2B_PRIVATE *out_private = NULL;
    TPM2B_PUBLIC *out_public = NULL;
    TPM2B_SENSITIVE_DATA *unsealed_data = NULL;
    TPM2B_DIGEST *policy_digest = NULL;

    printf("[+] Ініціалізація TCTI та контексту ESAPI...\n");
    rc = Tss2_TctiLdr_Initialize("device:/dev/tpmrm0", &tcti_ctx);
    CHECK_RC(rc, "Неможливо відкрити /dev/tpmrm0");

    rc = Esys_Initialize(&esys_ctx, tcti_ctx, NULL);
    CHECK_RC(rc, "Помилка ініціалізації Esys_Initialize");

    /* 1. Створення Primary Key у Owner ієрархії */
    TPM2B_PUBLIC in_public_primary = {
        .size = 0,
        .publicArea = {
            .type = TPM2_ALG_RSA,
            .nameAlg = TPM2_ALG_SHA256,
            .objectAttributes = (TPMA_OBJECT_USERWITHAUTH |
                                 TPMA_OBJECT_RESTRICTED |
                                 TPMA_OBJECT_DECRYPT |
                                 TPMA_OBJECT_FIXEDTPM |
                                 TPMA_OBJECT_FIXEDPARENT),
            .authPolicy = { .size = 0 },
            .parameters.rsaDetail = {
                .symmetric = {
                    .algorithm = TPM2_ALG_AES,
                    .keyBits.aes = 128,
                    .mode.aes = TPM2_ALG_CFB
                },
                .scheme = { .scheme = TPM2_ALG_NULL },
                .keyBits = 2048,
                .exponent = 0
            },
            .unique.rsa = { .size = 0 }
        }
    };

    printf("[+] Генерація Primary Key в ієрархії TPM2_RH_OWNER...\n");
    rc = Esys_CreatePrimary(
        esys_ctx, ESYS_TR_RH_OWNER,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        &in_public_primary, NULL, NULL,
        &primary_handle, NULL, NULL, NULL, NULL
    );
    CHECK_RC(rc, "Помилка виклику Esys_CreatePrimary");

    /* 2. Відкриття авторизаційної сесії політики */
    printf("[+] Відкриття авторизаційної сесії TPM2_SE_POLICY...\n");
    TPMT_SYM_DEF symmetric_def = {
        .algorithm = TPM2_ALG_NULL
    };
    rc = Esys_StartAuthSession(
        esys_ctx, ESYS_TR_NONE, ESYS_TR_NONE,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        NULL, TPM2_SE_POLICY, &symmetric_def, TPM2_ALG_SHA256,
        &session_handle
    );
    CHECK_RC(rc, "Помилка створення сесії політики");

    /* 3. Оцінка регістрів PCR 0 та PCR 7 у сесії */
    TPML_PCR_SELECTION pcr_selection = {
        .count = 1,
        .pcrSelections = {
            {
                .hash = TPM2_ALG_SHA256,
                .sizeofSelect = 3,
                .pcrSelect = { 0x81, 0x00, 0x00 } /* Біти 0 та 7 заповнені */
            }
        }
    };

    printf("[+] Оновлення digest політики через Esys_PolicyPCR (PCR 0, 7)...\n");
    rc = Esys_PolicyPCR(
        esys_ctx, session_handle,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        NULL, &pcr_selection
    );
    CHECK_RC(rc, "Помилка виконання Esys_PolicyPCR");

    /* 3a. Вилучення підсумкового PolicyDigest сесії */
    rc = Esys_PolicyGetDigest(
        esys_ctx, session_handle,
        ESYS_TR_NONE, ESYS_TR_NONE, ESYS_TR_NONE,
        &policy_digest
    );
    CHECK_RC(rc, "Помилка отримання PolicyDigest");

    /* 4. Запечатування секретних даних під зафіксовану політику */
    const char secret_payload[] = "MasterDiskKey-32-Bytes-Length!";
    TPM2B_SENSITIVE_CREATE in_sensitive = {
        .size = 0,
        .sensitive = {
            .userAuth = { .size = 0 },
            .data = {
                .size = sizeof(secret_payload),
                .buffer = { 0 }
            }
        }
    };
    memcpy(in_sensitive.sensitive.data.buffer, secret_payload, sizeof(secret_payload));

    TPM2B_PUBLIC in_public_seal = {
        .size = 0,
        .publicArea = {
            .type = TPM2_ALG_KEYEDHASH,
            .nameAlg = TPM2_ALG_SHA256,
            .objectAttributes = (TPMA_OBJECT_FIXEDTPM | TPMA_OBJECT_FIXEDPARENT),
            .authPolicy = { .size = 0 },
            .parameters.keyedHashDetail = {
                .scheme = { .scheme = TPM2_ALG_NULL }
            },
            .unique.keyedHash = { .size = 0 }
        }
    };

    /* Прив'язка об'єкта до розрахованої політики: без цього authPolicy порожній
       і об'єкт із знятим USERWITHAUTH не авторизується взагалі. */
    in_public_seal.publicArea.authPolicy = *policy_digest;

    printf("[+] Створення запечатаного об'єкта в TPM...\n");
    rc = Esys_Create(
        esys_ctx, primary_handle,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        &in_sensitive, &in_public_seal, NULL, NULL,
        &out_private, &out_public, NULL, NULL, NULL
    );
    CHECK_RC(rc, "Помилка запечатування секрету в Esys_Create");

    /* 5. Завантаження запечатаного об'єкта та виконання Unseal */
    rc = Esys_Load(
        esys_ctx, primary_handle,
        ESYS_TR_PASSWORD, ESYS_TR_NONE, ESYS_TR_NONE,
        out_private, out_public, &loaded_key_handle
    );
    CHECK_RC(rc, "Помилка завантаження запечатаного об'єкта");

    printf("[+] Виконання Esys_Unseal з використанням сесії політики...\n");
    rc = Esys_Unseal(
        esys_ctx, loaded_key_handle,
        session_handle, ESYS_TR_NONE, ESYS_TR_NONE,
        &unsealed_data
    );
    CHECK_RC(rc, "Помилка розпечатування даних (Unseal)");

    printf("[УСПІХ] Розпечатаний секрет: \"%s\"\n", unsealed_data->buffer);

cleanup:
    if (unsealed_data) Esys_Free(unsealed_data);
    if (policy_digest) Esys_Free(policy_digest);
    if (out_private) Esys_Free(out_private);
    if (out_public) Esys_Free(out_public);

    if (loaded_key_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, loaded_key_handle);
    if (session_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, session_handle);
    if (primary_handle != ESYS_TR_NONE) Esys_FlushContext(esys_ctx, primary_handle);

    if (esys_ctx) Esys_Finalize(&esys_ctx);
    if (tcti_ctx) Tss2_TctiLdr_Finalize(&tcti_ctx);

    return (rc == TSS2_RC_SUCCESS) ? EXIT_SUCCESS : EXIT_FAILURE;
}
