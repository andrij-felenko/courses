// Ідіоматична C++20 структура з упакованим вирівнюванням
#pragma pack(push, 1)
struct SignatureV2Hdr {
    uint8_t type;
    uint8_t version;
    uint8_t hash_algo;
    uint32_t keyid;      // Big-endian Key ID
    uint16_t sig_size;   // Big-endian розмір підпису
};
#pragma pack(pop)
