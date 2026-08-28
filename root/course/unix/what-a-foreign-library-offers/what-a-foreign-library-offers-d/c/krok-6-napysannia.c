#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>

int main(void) {
    const char message[] = "Unix library contract verification";
    unsigned char digest[EVP_MAX_MD_SIZE];
    size_t digest_len = 0;

    int ok = EVP_Q_digest(NULL, "SHA256", NULL, message, strlen(message), digest, &digest_len);
    if (!ok) {
        fprintf(stderr, "Помилка обчислення хешу SHA-256\n");
        return 1;
    }

    printf("SHA-256: ");
    for (size_t i = 0; i < digest_len; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");
    return 0;
}
