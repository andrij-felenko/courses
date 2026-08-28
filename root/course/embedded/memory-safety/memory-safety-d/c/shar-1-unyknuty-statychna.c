// ПОГАНО: купа на МК — фрагментація, можливий NULL, висячий покажчик
char *make_message(size_t n) {
    char *buf = malloc(n);          // а раптом NULL? а хто звільнить?
    // ...
    return buf;                     // викликач мусить пам'ятати про free()
}

// ДОБРЕ: статичний буфер фіксованого розміру — нічого не виділяємо
#define MSG_MAX 128
static char msg_buf[MSG_MAX];       // лінкер відвів місце ще при збірці

bool make_message(const char *src) {
    size_t len = strlen(src);
    if (len >= MSG_MAX) {           // перевірка МЕЖІ — умова (1)
        return false;               // не влізло — чесно кажемо «ні»
    }
    strcpy(msg_buf, src);           // тепер гарантовано влазить
    return true;
}
