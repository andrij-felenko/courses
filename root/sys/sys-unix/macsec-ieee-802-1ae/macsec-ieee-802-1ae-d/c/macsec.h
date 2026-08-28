/* Інтерфейс апаратного розвантаження MACsec у ядрі Linux (<net/macsec.h>) */
struct macsec_ops {
    int (*mdo_dev_open)(struct macsec_context *ctx);
    int (*mdo_dev_stop)(struct macsec_context *ctx);
    int (*mdo_add_secy)(struct macsec_context *ctx);
    int (*mdo_upd_secy)(struct macsec_context *ctx);
    int (*mdo_del_secy)(struct macsec_context *ctx);
    int (*mdo_add_rxsc)(struct macsec_context *ctx);
    int (*mdo_upd_rxsc)(struct macsec_context *ctx);
    int (*mdo_del_rxsc)(struct macsec_context *ctx);
    int (*mdo_add_rxsa)(struct macsec_context *ctx);
    int (*mdo_upd_rxsa)(struct macsec_context *ctx);
    int (*mdo_del_rxsa)(struct macsec_context *ctx);
    int (*mdo_add_txsa)(struct macsec_context *ctx);
    int (*mdo_upd_txsa)(struct macsec_context *ctx);
    int (*mdo_del_txsa)(struct macsec_context *ctx);
};
