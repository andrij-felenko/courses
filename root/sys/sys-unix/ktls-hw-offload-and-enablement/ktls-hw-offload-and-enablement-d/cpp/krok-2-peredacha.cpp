// Приклад на C++20 з використанням std::span
#include <linux/tls.h>
#include <cstring>
#include <span>
#include <system_error>

void set_ktls_tx_keys(int sock_fd, 
                      std::span<const uint8_t, 16> key,
                      std::span<const uint8_t, 8> iv,
                      std::span<const uint8_t, 4> salt,
                      uint64_t seq_num) {
    struct tls12_crypto_info_aes_gcm_128 info{};
    info.info.version = TLS_1_2_VERSION;
    info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    std::memcpy(info.key, key.data(), key.size());
    std::memcpy(info.iv, iv.data(), iv.size());
    std::memcpy(info.salt, salt.data(), salt.size());
    std::memcpy(info.rec_seq, &seq_num, sizeof(seq_num));

    if (::setsockopt(sock_fd, SOL_TLS, TLS_TX, &info, sizeof(info)) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка передачі TLS_TX ключів");
    }
}
