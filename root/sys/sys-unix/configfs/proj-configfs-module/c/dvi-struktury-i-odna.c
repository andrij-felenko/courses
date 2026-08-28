// SPDX-License-Identifier: GPL-2.0
#include <linux/configfs.h>
#include <linux/module.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/sysfs.h>

#define DEMO_LABEL_LEN 64
#define DEMO_LIMIT_MAX 1024

struct demo_target {
	struct config_group	group;		/* каталог t1/          */
	struct config_group	slots;		/* каталог t1/slots/    */
	unsigned int		limit;
	unsigned int		nr_links;
	char			label[DEMO_LABEL_LEN];
};

struct demo_slot {
	struct config_item	item;		/* каталог s0/          */
	unsigned int		weight;
};

static inline struct demo_target *to_demo_target(struct config_item *item)
{
	return container_of(to_config_group(item), struct demo_target, group);
}

static inline struct demo_target *slots_to_target(struct config_item *item)
{
	return container_of(to_config_group(item), struct demo_target, slots);
}

static inline struct demo_slot *to_demo_slot(struct config_item *item)
{
	return container_of(item, struct demo_slot, item);
}
