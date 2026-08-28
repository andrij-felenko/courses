/* Створення нового екземпляра індексу */
nn_status_t nn_index_create(const nn_config_t *config, nn_index_t **out_index);

/* Пакетна побудова індексу з лінійного буфера координат */
nn_status_t nn_index_build(nn_index_t *index,
                           const float *vectors_flat,
                           const int64_t *ids,
                           size_t count);

/* Динамічне додавання одного вектора */
nn_status_t nn_index_insert(nn_index_t *index,
                            int64_t id,
                            const float *vector);

/* Пошук k найближчих сусідів */
nn_status_t nn_index_search_knn(const nn_index_t *index,
                                const float *query,
                                size_t k,
                                nn_result_set_t *out_result,
                                nn_search_stats_t *out_stats);

/* Радіусний пошук (Range Search) */
nn_status_t nn_index_search_radius(const nn_index_t *index,
                                   const float *query,
                                   float radius,
                                   nn_result_set_t *out_result,
                                   nn_search_stats_t *out_stats);

/* Вивільнення ресурсів */
void nn_index_free(nn_index_t *index);
