export module crypto.aes;

export class AesEncryptor {
public:
    AesEncryptor();
    void set_key(const char* key, int len);
    void encrypt_block(const void* in, void* out);
private:
    void expand_key_schedule();
};

// Межа приватного фрагмента: усе нижче цього рядка не потрапляє у відкритий BMI
module :private;

AesEncryptor::AesEncryptor() = default;

void AesEncryptor::set_key(const char* key, int len) {
    expand_key_schedule();
}

void AesEncryptor::expand_key_schedule() {
    // Внутрішня важка криптографічна математика
}

void AesEncryptor::encrypt_block(const void* in, void* out) {
    // Операції над байтами
}
