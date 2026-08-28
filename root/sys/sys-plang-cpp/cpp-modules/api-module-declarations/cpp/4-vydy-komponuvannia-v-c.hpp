export module cryptography;

// 1. Internal Linkage: унікальна для цього файлу, не конфліктує з іншими static-функціями
static void mix_entropy(uint64_t* state);

// 2. Module Linkage: доступна всім файлам модуля cryptography, але невидима для імпортерів
void generate_prime_candidate(mpz_t out);

// 3. External Linkage: публічний контракт модуля для зовнішніх споживачів
export void generate_rsa_keypair(PublicKey* pub, PrivateKey* priv);
