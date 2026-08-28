typedef void (*dr_release_t)(struct device *dev, void *res);

struct devres_node {
	struct list_head	entry;      /* місце в списку пристрою */
	dr_release_t		release;    /* чим це звільняти */
	/* під CONFIG_DEBUG_DEVRES тут ще ім'я й розмір */
};

struct devres {
	struct devres_node	node;
	u8			data[];     /* корисне навантаження */
};
