/* Перелічення атрибутів SA в <linux/if_macsec.h> */
enum enum_macsec_sa_attrs {
    MACSEC_SA_ATTR_UNSPEC,
    MACSEC_SA_ATTR_AN,        /* u8: Номер асоціації (Association Number: 0..3) */
    MACSEC_SA_ATTR_ACTIVE,    /* u8: 1 = SA активна для шифрування, 0 = неактивна */
    MACSEC_SA_ATTR_PN,        /* u32 або u64 (для XPN): Початковий/поточний номер пакета */
    MACSEC_SA_ATTR_KEYID,     /* 16 байт: Ідентифікатор ключа (Key ID / CKN) */
    MACSEC_SA_ATTR_KEY,       /* 16/32 байти: Секретний ключ SAK (AES-128 або AES-256) */
    MACSEC_SA_ATTR_STATS,     /* Вкладений атрибут статистики цієї конкретної SA */
    MACSEC_SA_ATTR_PAD,
    __MACSEC_SA_ATTR_END,
};
