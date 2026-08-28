/* OID для кривої secp256r1 / NIST P-256: 1.2.840.10045.3.1.7 */
static CK_BYTE ec_p256_params[] = {
    0x06, 0x08, 0x2A, 0x86, 0x48, 0xCE, 0x3D, 0x03, 0x01, 0x07
};

CK_BBOOL bTrue  = CK_TRUE;
CK_BBOOL bFalse = CK_FALSE;
char privLabel[] = "Secure-Device-ECDSA-Key";
char pubLabel[]  = "Secure-Device-ECDSA-PubKey";

CK_ATTRIBUTE pubTemplate[] = {
    { CKA_TOKEN,         &bTrue,             sizeof(bTrue) },
    { CKA_VERIFY,        &bTrue,             sizeof(bTrue) },
    { CKA_ECDSA_PARAMS,  ec_p256_params,     sizeof(ec_p256_params) },
    { CKA_LABEL,         pubLabel,           strlen(pubLabel) }
};

CK_ATTRIBUTE privTemplate[] = {
    { CKA_TOKEN,         &bTrue,             sizeof(bTrue) },
    { CKA_PRIVATE,       &bTrue,             sizeof(bTrue) },
    { CKA_SENSITIVE,     &bTrue,             sizeof(bTrue) },
    { CKA_EXTRACTABLE,   &bFalse,            sizeof(bFalse) }, /* Заборона експорту назавжди */
    { CKA_SIGN,          &bTrue,             sizeof(bTrue) },
    { CKA_LABEL,         privLabel,          strlen(privLabel) }
};
