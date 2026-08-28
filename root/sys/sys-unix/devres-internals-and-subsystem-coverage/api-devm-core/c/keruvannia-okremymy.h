void *devres_alloc(dr_release_t release, size_t size, gfp_t gfp);
void devres_add(struct device *dev, void *res);
void devres_free(void *res);
int devres_destroy(struct device *dev, dr_release_t release,
                   dr_match_t match, void *match_data);
int devres_release(struct device *dev, dr_release_t release,
                   dr_match_t match, void *match_data);
void *devres_find(struct device *dev, dr_release_t release,
                  dr_match_t match, void *match_data);
void *devres_get(struct device *dev, void *new_res,
                 dr_match_t match, void *match_data);
void *devres_remove(struct device *dev, dr_release_t release,
                    dr_match_t match, void *match_data);
