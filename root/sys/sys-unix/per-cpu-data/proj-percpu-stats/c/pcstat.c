/* pcstat.c — статистика per-CPU: лічильники, запас, гак на вимикання ядра */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/init.h>
#include <linux/percpu.h>
#include <linux/local_lock.h>
#include <linux/list.h>
#include <linux/slab.h>
#include <linux/timer.h>
#include <linux/jiffies.h>
#include <linux/debugfs.h>
#include <linux/seq_file.h>
#include <linux/kstrtox.h>
#include <linux/cpu.h>
#include <linux/cpuhotplug.h>
#include <linux/spinlock.h>

struct pcstat_counters {
    u64 events;      /* скільки разів спрацював гарячий шлях      */
    u64 bytes;       /* скільки байтів він при цьому «обробив»    */
    u64 misses;      /* скільки разів запас виявився порожнім     */
    u64 refills;     /* скільки об'єктів довелося виділити наново */
};

static DEFINE_PER_CPU(struct pcstat_counters, pcstat_cnt);
