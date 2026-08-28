#define list_lru_init(lru)                 __list_lru_init((lru), false, NULL, NULL)
#define list_lru_init_memcg(lru, shrinker) __list_lru_init((lru), true,  NULL, shrinker)
void list_lru_destroy(struct list_lru *lru);

bool list_lru_add_obj(struct list_lru *lru, struct list_head *item);
bool list_lru_del_obj(struct list_lru *lru, struct list_head *item);

unsigned long list_lru_count_one(struct list_lru *lru, int nid, struct mem_cgroup *memcg);
unsigned long list_lru_count_node(struct list_lru *lru, int nid);
unsigned long list_lru_shrink_count(struct list_lru *lru, struct shrink_control *sc);
unsigned long list_lru_shrink_walk(struct list_lru *lru, struct shrink_control *sc,
                                   list_lru_walk_cb isolate, void *cb_arg);

typedef enum lru_status (*list_lru_walk_cb)(struct list_head *item,
                                            struct list_lru_one *list,
                                            spinlock_t *lock, void *cb_arg);
