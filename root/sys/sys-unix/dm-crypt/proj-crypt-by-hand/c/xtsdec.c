/* gcc -O2 -o xtsdec xtsdec.c -lcrypto
   ужиток: ./xtsdec disk.img key.bin 2048 100 > back.bin                     */
#define _FILE_OFFSET_BITS 64
#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>

#define SECTOR 512

int main(int argc, char **argv)
{
    unsigned char key[64], iv[16] = {0}, ct[SECTOR], pt[SECTOR];
    unsigned long long hdr, sect;
    EVP_CIPHER_CTX *ctx;
    FILE *f;
    int n, i;

    if (argc != 5)
        return fprintf(stderr, "ужиток: %s образ ключ hdr сектор\n", argv[0]), 2;
    hdr  = strtoull(argv[3], NULL, 10);
    sect = strtoull(argv[4], NULL, 10);

    if (!(f = fopen(argv[2], "rb")) || fread(key, 1, sizeof key, f) != sizeof key)
        return perror("ключ"), 1;
    fclose(f);

    f = fopen(argv[1], "rb");                              /* МІСЦЕ */
    if (!f || fseeko(f, (off_t)((hdr + sect) * SECTOR), SEEK_SET) != 0
           || fread(ct, 1, SECTOR, f) != SECTOR)
        return perror("образ"), 1;
    fclose(f);

    for (i = 0; i < 8; i++)                                /* ЗМІНА: plain64 */
        iv[i] = (unsigned char)(sect >> (8 * i));

    ctx = EVP_CIPHER_CTX_new();
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_xts(), NULL, key, iv) != 1
        || EVP_DecryptUpdate(ctx, pt, &n, ct, SECTOR) != 1)  /* увесь сектор за раз */
        return fprintf(stderr, "EVP відмовив\n"), 1;
    EVP_CIPHER_CTX_free(ctx);

    fwrite(pt, 1, (size_t)n, stdout);
    return 0;
}
