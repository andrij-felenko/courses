int  pm_genpd_init(struct generic_pm_domain *genpd,
                   struct dev_power_governor *gov, bool is_off);
int  pm_genpd_remove(struct generic_pm_domain *genpd);

int  pm_genpd_add_subdomain(struct generic_pm_domain *genpd,
                            struct generic_pm_domain *subdomain);
int  pm_genpd_remove_subdomain(struct generic_pm_domain *genpd,
                               struct generic_pm_domain *subdomain);

int  of_genpd_add_provider_simple(struct device_node *np,
                                  struct generic_pm_domain *genpd);
int  of_genpd_add_provider_onecell(struct device_node *np,
                                   struct genpd_onecell_data *data);
void of_genpd_del_provider(struct device_node *np);

int  of_genpd_parse_idle_states(struct device_node *dn,
                                struct genpd_power_state **states, int *n);

int  pm_genpd_add_device(struct generic_pm_domain *genpd, struct device *dev);
int  pm_genpd_remove_device(struct device *dev);
