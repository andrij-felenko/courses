/* Header C: struct mptcpd_plugin_ops */
struct mptcpd_plugin_ops {
    void (*new_connection)(struct mptcpd_pm *pm, uint32_t token, ...);
    void (*connection_established)(struct mptcpd_pm *pm, uint32_t token, ...);
    void (*connection_closed)(struct mptcpd_pm *pm, uint32_t token, ...);
    void (*new_address)(struct mptcpd_pm *pm, uint32_t token, mptcpd_aid_t id, ...);
    void (*address_removed)(struct mptcpd_pm *pm, uint32_t token, mptcpd_aid_t id, ...);
    void (*new_subflow)(struct mptcpd_pm *pm, uint32_t token, ...);
    void (*subflow_closed)(struct mptcpd_pm *pm, uint32_t token, ...);
};
