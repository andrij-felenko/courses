#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <keyutils.h>

/* Збереження logon-ключа для fscrypt / dm-crypt у сесійній в'язці */
key_serial_t store_logon_secret(const char *key_desc, const void *raw_key, size_t key_len) {
    /* add_key(type, description, payload, plen, keyring) */
    key_serial_t key_id = add_key("logon", key_desc, raw_key, key_len, KEY_SPEC_SESSION_KEYRING);
    
    if (key_id == -1) {
        perror("add_key failed");
        return -1;
    }
    
    printf("Ключ успішно додано. Serial ID: %d\n", key_id);
    return key_id;
}
