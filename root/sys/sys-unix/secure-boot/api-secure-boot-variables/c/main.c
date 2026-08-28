typedef struct {
    EFI_GUID  SignatureType;        // 16 Б — що саме тут лежить
    UINT32    SignatureListSize;    // увесь список разом із цим заголовком
    UINT32    SignatureHeaderSize;  // 0 для всіх чинних типів
    UINT32    SignatureSize;        // розмір ОДНОГО запису
 // UINT8     SignatureHeader[SignatureHeaderSize];
 // EFI_SIGNATURE_DATA Signatures[];
} EFI_SIGNATURE_LIST;

typedef struct {
    EFI_GUID  SignatureOwner;       // 16 Б — хто вніс цей запис
    UINT8     SignatureData[];      // сертифікат DER або хеш
} EFI_SIGNATURE_DATA;
