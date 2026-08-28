// Формати точок для кривої BLS12-381 (Field p size = 381 bits / 48 bytes)
#define BLS12_381_FP_BYTES        48
#define BLS12_381_FP2_BYTES       96   // 2 * 48 bytes (c0, c1)
#define BLS12_381_G2_UNCOMPRESSED 192  // (x, y) in FP2 = 2 * 96 bytes
#define BLS12_381_G2_COMPRESSED   96   // x in FP2 + flags in top bits

// Формати точок для кривої BN254 / alt_bn128 (Field p size = 254 bits / 32 bytes)
#define BN254_FP_BYTES            32
#define BN254_FP2_BYTES           64   // 2 * 32 bytes
#define BN254_G2_UNCOMPRESSED     128  // (x, y) in FP2 = 2 * 64 bytes
#define BN254_G2_COMPRESSED       64   // x in FP2 + sign bit
