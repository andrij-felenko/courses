CK_RV C_GenerateKeyPair(
    CK_SESSION_HANDLE    hSession,                    /* Дескриптор RW-сесії */
    CK_MECHANISM_PTR     pMechanism,                  /* CKM_EC_KEY_PAIR_GEN або CKM_RSA_PKCS_KEY_PAIR_GEN */
    CK_ATTRIBUTE_PTR     pPublicKeyTemplate,          /* Шаблон відкритого ключа */
    CK_ULONG             ulPublicKeyAttributeCount,   /* Кількість атрибутів відкритого ключа */
    CK_ATTRIBUTE_PTR     pPrivateKeyTemplate,         /* Шаблон приватного ключа */
    CK_ULONG             ulPrivateKeyAttributeCount,  /* Кількість атрибутів приватного ключа */
    CK_OBJECT_HANDLE_PTR phPublicKey,                 /* Дескриптор згенерованого PubKey */
    CK_OBJECT_HANDLE_PTR phPrivateKey                 /* Дескриптор згенерованого PrivKey */
);
