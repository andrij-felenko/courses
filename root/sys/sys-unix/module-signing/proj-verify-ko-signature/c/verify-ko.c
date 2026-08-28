/* verify-ko.c — повторення ядрової перевірки підпису модуля
 * збирання: cc -O2 -Wall -o verify-ko verify-ko.c -lcrypto        */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>          /* ntohl */
#include <sys/mman.h>
#include <sys/stat.h>

#include <openssl/bio.h>
#include <openssl/bn.h>
#include <openssl/cms.h>
#include <openssl/err.h>
#include <openssl/objects.h>
#include <openssl/pem.h>
#include <openssl/x509.h>

#define MARKER      "~Module signature appended~\n"
#define MARKER_LEN  (sizeof(MARKER) - 1)        /* 28 */

/* дослівно з include/uapi/linux/module_signature.h */
struct module_signature {
    uint8_t  algo;          /* завжди 0 */
    uint8_t  hash;          /* завжди 0 */
    uint8_t  id_type;       /* 2 = MODULE_SIGNATURE_TYPE_PKCS7 */
    uint8_t  signer_len;    /* завжди 0 */
    uint8_t  key_id_len;    /* завжди 0 */
    uint8_t  pad[3];        /* у ядрі зветься __pad, завжди нулі */
    uint32_t sig_len;       /* мережевий порядок байтів! */
};
_Static_assert(sizeof(struct module_signature) == 12, "опис мусить бути 12 Б");

static void die(const char *msg)
{
    fprintf(stderr, "%s\n", msg);
    ERR_print_errors_fp(stderr);
    exit(1);
}

/* Ім'я підписанта й алгоритм хешування. Читається з самого повідомлення,
 * без жодного сертифіката.                                               */
static void print_signer(CMS_ContentInfo *cms)
{
    STACK_OF(CMS_SignerInfo) *sis = CMS_get0_SignerInfos(cms);
    if (!sis || sk_CMS_SignerInfo_num(sis) < 1)
        die("у повідомленні немає жодного підписанта");

    for (int i = 0; i < sk_CMS_SignerInfo_num(sis); i++) {
        CMS_SignerInfo  *si    = sk_CMS_SignerInfo_value(sis, i);
        ASN1_OCTET_STRING *kid = NULL;
        X509_NAME      *issuer = NULL;
        ASN1_INTEGER      *sno = NULL;

        if (!CMS_SignerInfo_get0_signer_id(si, &kid, &issuer, &sno))
            die("не читається ідентифікатор підписанта");

        if (issuer) {
            char   *name = X509_NAME_oneline(issuer, NULL, 0);
            BIGNUM *bn   = ASN1_INTEGER_to_BN(sno, NULL);
            char   *hex  = BN_bn2hex(bn);
            printf("підписант: видавець %s\n           серійний %s\n", name, hex);
            OPENSSL_free(hex); BN_free(bn); OPENSSL_free(name);
        } else if (kid) {
            const unsigned char *p = ASN1_STRING_get0_data(kid);
            int n = ASN1_STRING_length(kid);
            printf("підписант: ідентифікатор ключа ");
            for (int j = 0; j < n; j++) printf("%02x", p[j]);
            putchar('\n');
        }

        /* яким хешем підписано — це те, чого ядро може не вміти */
        X509_ALGOR *dig = NULL;
        CMS_SignerInfo_get0_algs(si, NULL, NULL, &dig, NULL);
        if (dig) {
            const ASN1_OBJECT *oid = NULL;
            char buf[80];
            X509_ALGOR_get0(&oid, NULL, NULL, dig);
            OBJ_obj2txt(buf, sizeof(buf), oid, 0);
            printf("хеш:       %s\n", buf);
        }
    }
}

static X509 *load_cert(const char *path)
{
    BIO *b = BIO_new_file(path, "rb");
    if (!b) die("сертифікат не відкривається");

    X509 *c = PEM_read_bio_X509(b, NULL, NULL, NULL);
    if (!c) {                       /* не PEM — пробуємо як сирий DER */
        ERR_clear_error();
        BIO_reset(b);
        c = d2i_X509_bio(b, NULL);
    }
    BIO_free(b);
    if (!c) die("сертифікат не читається ні як PEM, ні як DER");
    return c;
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "вжиток: %s <модуль.ko> [сертифікат.pem|.der]\n", argv[0]);
        return 2;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) { perror(argv[1]); return 1; }

    struct stat st;
    if (fstat(fd, &st) < 0) { perror("fstat"); return 1; }
    size_t len = (size_t)st.st_size;

    if (len <= MARKER_LEN + sizeof(struct module_signature)) {
        printf("файл закороткий, щоб узагалі мати підпис\n");
        return 1;
    }

    const unsigned char *map = mmap(NULL, len, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) { perror("mmap"); return 1; }
    close(fd);                      /* відображення живе й без дескриптора */

    /* 1. маркер у самому кінці */
    if (memcmp(map + len - MARKER_LEN, MARKER, MARKER_LEN) != 0) {
        printf("маркера немає — для ядра це непідписаний файл (-ENODATA)\n");
        return 1;
    }

    /* 2. опис підпису — рівно перед маркером */
    struct module_signature ms;
    memcpy(&ms, map + len - MARKER_LEN - sizeof(ms), sizeof(ms));

    if (ms.id_type != 2) {
        printf("опис каже не про PKCS#7 (id_type=%u) — ядро дало б -ENOPKG\n",
               ms.id_type);
        return 1;
    }
    if (ms.algo || ms.hash || ms.signer_len || ms.key_id_len ||
        ms.pad[0] || ms.pad[1] || ms.pad[2]) {
        printf("в описі ненульові поля — ядро дало б -EBADMSG\n");
        return 1;
    }

    size_t sig_len = ntohl(ms.sig_len);          /* ← без цього все розсиплеться */
    size_t tail    = MARKER_LEN + sizeof(ms) + sig_len;
    if (tail >= len) {
        printf("довжина підпису більша за сам файл — -EBADMSG\n");
        return 1;
    }
    size_t body = len - tail;

    printf("розкладка: тіло %zu + підпис %zu + опис %zu + маркер %zu = %zu\n",
           body, sig_len, sizeof(ms), MARKER_LEN, len);

    /* 3. розбір повідомлення CMS */
    BIO *sig_bio = BIO_new_mem_buf(map + body, (int)sig_len);
    CMS_ContentInfo *cms = d2i_CMS_bio(sig_bio, NULL);
    if (!cms) die("повідомлення CMS не розбирається");

    print_signer(cms);

    int rc = 0;
    if (argc == 3) {
        /* 4. звірка підпису з поданим сертифікатом */
        STACK_OF(X509) *certs = sk_X509_new_null();
        sk_X509_push(certs, load_cert(argv[2]));

        BIO *body_bio = BIO_new_mem_buf(map, (int)body);

        int ok = CMS_verify(cms, certs, NULL, body_bio, NULL,
                            CMS_NO_SIGNER_CERT_VERIFY | CMS_BINARY | CMS_NOINTERN);
        if (ok == 1) {
            printf("ПІДПИС ЗБІГСЯ\n");
        } else {
            printf("ПІДПИС НЕ ЗБІГСЯ\n");
            ERR_print_errors_fp(stderr);
            rc = 1;
        }
        BIO_free(body_bio);
        sk_X509_pop_free(certs, X509_free);
    } else {
        printf("сертифіката не подано — звіряти нема з чим\n");
    }

    CMS_ContentInfo_free(cms);
    BIO_free(sig_bio);
    munmap((void *)map, len);
    return rc;
}
