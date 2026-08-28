enum {
    ETHTOOL_A_RSS_UNSPEC,
    ETHTOOL_A_RSS_HEADER,       /* Вкладений заголовок (ETHTOOL_A_HEADER_*) */
    ETHTOOL_A_RSS_CONTEXT,      /* u32: Ідентифікатор RSS-контексту */
    ETHTOOL_A_RSS_HFUNC,        /* u32: Хеш-функція (ETH_RSS_HASH_*) */
    ETHTOOL_A_RSS_INDIR,        /* Binary/Array: Масив u32 комірок RETA */
    ETHTOOL_A_RSS_HKEY,         /* Binary: Байтовий масив секретного ключа */
    __ETHTOOL_A_RSS_CNT,
    ETHTOOL_A_RSS_MAX = (__ETHTOOL_A_RSS_CNT - 1)
};
