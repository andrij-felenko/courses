/* Скорочено за заголовком ядра include/linux/usb/typec.h */
struct typec_capability {
    enum typec_port_type    type;           /* TYPEC_PORT_SRC, TYPEC_PORT_SNK, TYPEC_PORT_DRP */
    enum typec_port_data    data;           /* TYPEC_PORT_DFP, TYPEC_PORT_UFP, TYPEC_PORT_DRD */
    u16                     revision;       /* Версія специфікації Type-C у BCD: 0x0130 = 1.3 */
    u16                     pd_revision;    /* Версія специфікації USB PD у BCD: 0x0300 = 3.0 */

    const struct typec_operations *ops;     /* Покажчик на функції зворотного виклику (callback ops) */
    
    struct fwnode_handle   *fwnode;         /* Зв'язок із вузлом Device Tree або ACPI */
    void                   *driver_data;    /* Приватні дані драйвера контролера */

    int                     prefer_role;    /* Бажана роль при підключенні: Try.SRC / Try.SNK */
};
