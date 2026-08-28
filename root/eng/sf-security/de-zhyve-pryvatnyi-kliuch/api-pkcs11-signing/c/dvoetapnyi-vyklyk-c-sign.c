/* Крок 1: Запит необхідного розміру підпису */
CK_ULONG sigLen = 0;
CK_RV rv = C_Sign(hSession, digest, 32, NULL, &sigLen);
if (rv != CKR_OK) {
    /* Обробка помилки */
}

/* Крок 2: Виділення пам'яті під буфер та отримання підпису */
CK_BYTE *signature = (CK_BYTE *)malloc(sigLen);
rv = C_Sign(hSession, digest, 32, signature, &sigLen);
if (rv == CKR_OK) {
    /* Підпис успішно накладено в апаратному чипі */
}
