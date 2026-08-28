// crypto.c
// static обмежує видимість цим файлом:
static int s_private_seed = 42;

static int internal_hash(int val) {
    return val ^ s_private_seed;
}

int public_encrypt(int raw) {
    return internal_hash(raw);
}
