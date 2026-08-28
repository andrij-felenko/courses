struct cred {
    atomic_t        usage;
    kuid_t          uid;            /* Реальний ідентифікатор користувача (ruid) */
    kgid_t          gid;            /* Реальний ідентифікатор групи (rgid) */
    kuid_t          suid;           /* Збережений ідентифікатор користувача (suid) */
    kgid_t          sgid;           /* Збережений ідентифікатор групи (sgid) */
    kuid_t          euid;           /* Ефективний ідентифікатор користувача (euid) */
    kgid_t          egid;           /* Ефективний ідентифікатор групи (egid) */
    kuid_t          fsuid;          /* Ідентифікатор користувача для файлової системи (fsuid) */
    kgid_t          fsgid;          /* Ідентифікатор групи для файлової системи (fsgid) */
    unsigned        securebits;     /* Прапорці фіксації привілеїв (SECURE_* прапорці) */
    kernel_cap_t    cap_inheritable;/* Capabilities, що успадковуються через execve */
    kernel_cap_t    cap_permitted;  /* Дозволені capabilities (максимальний набір) */
    kernel_cap_t    cap_effective;  /* Активні capabilities, що перевіряються ядром */
    kernel_cap_t    cap_bset;       /* Обмежувальний набір (bounding set) */
    kernel_cap_t    cap_ambient;    /* Амбієнтні capabilities для не-привілейованих бінарників */
    struct group_info *group_info;  /* Масив додаткових числових GID (Supplementary Groups) */
    struct user_struct *user;       /* Статистика споживання ресурсів користувачем */
    struct user_namespace *user_ns; /* Простір імен користувачів (User Namespace) */
};
