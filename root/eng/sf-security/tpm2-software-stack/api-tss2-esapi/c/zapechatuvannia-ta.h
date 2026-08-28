/* Виклики створення, завантаження та розпечатування секрету в ESAPI */
TSS2_RC Esys_Create(
    ESYS_CONTEXT *esysContext, ESYS_TR parentHandle,
    ESYS_TR shandle1, ESYS_TR shandle2, ESYS_TR shandle3,
    const TPM2B_SENSITIVE_CREATE *inSensitive, const TPM2B_PUBLIC *inPublic,
    const TPM2B_DATA *outsideInfo, const TPML_PCR_SELECTION *creationPCR,
    TPM2B_PRIVATE **outPrivate, TPM2B_PUBLIC **outPublic,
    TPM2B_CREATION_DATA **creationData, TPM2B_DIGEST **creationHash, TPMT_TK_CREATION **creationTicket
);

TSS2_RC Esys_Load(
    ESYS_CONTEXT *esysContext, ESYS_TR parentHandle,
    ESYS_TR shandle1, ESYS_TR shandle2, ESYS_TR shandle3,
    const TPM2B_PRIVATE *inPrivate, const TPM2B_PUBLIC *inPublic, ESYS_TR *objectHandle
);

TSS2_RC Esys_Unseal(
    ESYS_CONTEXT *esysContext, ESYS_TR itemHandle,
    ESYS_TR shandle1, ESYS_TR shandle2, ESYS_TR shandle3, TPM2B_SENSITIVE_DATA **outData
);
