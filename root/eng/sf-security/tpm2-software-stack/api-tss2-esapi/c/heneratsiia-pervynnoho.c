TSS2_RC Esys_CreatePrimary(
    ESYS_CONTEXT *esysContext,
    ESYS_TR primaryHandle,           // ESYS_TR_RH_OWNER або ESYS_TR_RH_ENDORSEMENT
    ESYS_TR shandle1,                 // ESYS_TR_PASSWORD або дескриптор сесії
    ESYS_TR shandle2,                 // ESYS_TR_NONE
    ESYS_TR shandle3,                 // ESYS_TR_NONE
    const TPM2B_PUBLIC *inPublic,     // Шаблон параметрів ключа
    const TPM2B_DATA *outsideInfo,    // Ефемерні зовнішні дані (Nonce) або NULL
    const TPML_PCR_SELECTION *creationPCR, // Список PCR для фіксації створення
    ESYS_TR *objectHandle,            // Вихідний дескриптор створеного ключа
    TPM2B_PUBLIC **outPublic,         // Згенерована публічна частина ключа
    TPM2B_CREATION_DATA **creationData,
    TPM2B_DIGEST **creationHash,
    TPMT_TK_CREATION **creationTicket
);
