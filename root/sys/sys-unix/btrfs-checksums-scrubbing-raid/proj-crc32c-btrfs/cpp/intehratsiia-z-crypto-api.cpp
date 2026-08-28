// C++ RAII-обгортка для керування хендлом Kernel Crypto API
#include <memory>
#include <stdexcept>
#include <crypto/hash.h>

struct CryptoShashDeleter {
    void operator()(struct crypto_shash* tfm) const {
        if (tfm && !IS_ERR(tfm)) {
            crypto_free_shash(tfm);
        }
    }
};

using CryptoShashPtr = std::unique_ptr<struct crypto_shash, CryptoShashDeleter>;

CryptoShashPtr createBtrfsHasher() {
    struct crypto_shash* tfm = crypto_alloc_shash("crc32c", 0, 0);
    if (IS_ERR(tfm)) {
        throw std::runtime_error("BTRFS: не вдалося ініціалізувати crc32c crypto handle");
    }
    return CryptoShashPtr(tfm);
}
