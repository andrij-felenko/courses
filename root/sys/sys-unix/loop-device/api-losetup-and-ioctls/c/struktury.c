struct loop_info64 {
        __u64 lo_device;                    /* лише читання: пристрій, де лежить файл */
        __u64 lo_inode;                     /* лише читання: номер inode файлу */
        __u64 lo_rdevice;                   /* лише читання: якщо носій сам є пристроєм */
        __u64 lo_offset;                    /* зсув початку даних у файлі, байти */
        __u64 lo_sizelimit;                 /* скільки байтів видно; 0 — до кінця файлу */
        __u32 lo_number;                    /* лише читання: N у /dev/loopN */
        __u32 lo_encrypt_type;              /* мусить бути LO_CRYPT_NONE (0) */
        __u32 lo_encrypt_key_size;          /* мусить бути ≤ LO_KEY_SIZE (32) */
        __u32 lo_flags;                     /* LO_FLAGS_* */
        __u8  lo_file_name[LO_NAME_SIZE];   /* 64 байти: те, що видно в backing_file */
        __u8  lo_crypt_name[LO_NAME_SIZE];
        __u8  lo_encrypt_key[LO_KEY_SIZE];
        __u64 lo_init[2];
};
