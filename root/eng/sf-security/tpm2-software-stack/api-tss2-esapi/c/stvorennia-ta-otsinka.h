TSS2_RC Esys_StartAuthSession(
    ESYS_CONTEXT *esysContext,
    ESYS_TR tpmKey, ESYS_TR bind,
    ESYS_TR shandle1, ESYS_TR shandle2, ESYS_TR shandle3,
    const TPM2B_NONCE *nonceCaller,
    TPM2_SE sessionType,             // TPM2_SE_POLICY або TPM2_SE_HMAC
    const TPMT_SYM_DEF *symmetric,   // Параметри шифрування сесії (напр., AES-128-CFB)
    TPMI_ALG_HASH authHash,          // TPM2_ALG_SHA256
    ESYS_TR *sessionHandle
);

TSS2_RC Esys_PolicyPCR(
    ESYS_CONTEXT *esysContext,
    ESYS_TR policySession,
    ESYS_TR shandle1, ESYS_TR shandle2, ESYS_TR shandle3,
    const TPM2B_DIGEST *pcrDigest,   // Очікуване значення гешу або NULL для поточних PCR
    const TPML_PCR_SELECTION *pcrs   // Маска вимірюваних регістрів PCR
);
