#define OPAL_KEY_MAX    256
#define OPAL_MAX_LRS    9
#define OPAL_UID_LENGTH 8

struct opal_key {
        __u8 lr;                  /* номер діапазону; 0 — глобальний */
        __u8 key_len;             /* довжина пароля в байтах */
        __u8 key_type;            /* OPAL_INCLUDED | OPAL_KEYRING */
        __u8 __align[5];
        __u8 key[OPAL_KEY_MAX];
};
