/* Контрольне повідомлення для вектора ініціалізації (IV) */
struct af_alg_iv {
    __u32   ivlen;      /* Довжина IV у байтах (наприклад, 16 для AES-CBC) */
    __u8    iv[0];      /* Блок IV (гнучкий масив байтів) */
};

/* Напрямок операції (передається як __u32 у макросі CMSG_DATA) */
#define ALG_OP_DECRYPT  0
#define ALG_OP_ENCRYPT  1

/* Нумерація спільна для optname у setsockopt() і для cmsg_type (рівень SOL_ALG) */
#define ALG_SET_KEY           1 /* setsockopt: ключ байтами */
#define ALG_SET_IV            2 /* Приймає struct af_alg_iv + байти вектора ініціалізації */
#define ALG_SET_OP            3 /* Приймає __u32: ALG_OP_ENCRYPT або ALG_OP_DECRYPT */
#define ALG_SET_AEAD_ASSOCLEN 4 /* Приймає __u32: довжина автентифікованих даних (AAD) */
#define ALG_SET_AEAD_AUTHSIZE 5 /* setsockopt: довжина тегу автентифікації */
