/* Структура вузла інтернованої мітки у ядрі Linux (security/smack/smack.h) */
struct smack_known {
    struct list_head    list;
    struct hlist_node   smk_hashed;
    char               *smk_known;
    u32                 smk_secid;
    struct netlbl_lsm_secattr smk_netlabel;
    struct list_head    smk_rules;
    struct mutex        smk_rules_lock;
};
