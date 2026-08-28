// SPDX-License-Identifier: GPL-2.0
/* cpucache.c — per-CPU запас об'єктів і пара колбеків гарячого підключення */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/cpu.h>
#include <linux/cpuhotplug.h>
#include <linux/debugfs.h>
#include <linux/init.h>
#include <linux/kstrtox.h>
#include <linux/local_lock.h>
#include <linux/module.h>
#include <linux/percpu.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

#define WANT 8            /* скільки об'єктів тримає запас одного ядра процесора */

struct obj {
        struct obj *next;
};

/* ── спільний пул: один на систему, під звичайним спінлоком ─────────── */
static DEFINE_SPINLOCK(pool_lock);
static struct obj *pool_head;
static unsigned long pool_size;

static void obj_list_free(struct obj *list)
{
        while (list) {
                struct obj *o = list;

                list = o->next;
                kfree(o);
        }
}

static void pool_push(struct obj *o)
{
        spin_lock(&pool_lock);
        o->next = pool_head;
        pool_head = o;
        pool_size++;
        spin_unlock(&pool_lock);
}

static struct obj *pool_pop(void)
{
        struct obj *o;

        spin_lock(&pool_lock);
        o = pool_head;
        if (o) {
                pool_head = o->next;
                pool_size--;
        }
        spin_unlock(&pool_lock);

        return o ? o : kmalloc(sizeof(*o), GFP_KERNEL);
}

/* ── запас на кожному ядрі процесора ────────────────────────────────── */
struct cache {
        local_lock_t  lock;
        struct obj   *head;
        unsigned int  count;
        unsigned long hits, misses, filled, drained;
};

static DEFINE_PER_CPU(struct cache, cache) = {
        .lock = INIT_LOCAL_LOCK(lock),
};

static struct obj *obj_get(void)
{
        struct cache *c;
        struct obj *o;

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        o = c->head;
        if (o) {
                c->head = o->next;
                c->count--;
                c->hits++;
        } else {
                c->misses++;
        }
        local_unlock(&cache.lock);

        return o ? o : pool_pop();   /* у пул ідемо вже без замка: там можна заснути */
}

static void obj_put(struct obj *o)
{
        struct cache *c;
        bool kept;

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        kept = c->count < WANT;
        if (kept) {
                o->next = c->head;
                c->head = o;
                c->count++;
        }
        local_unlock(&cache.lock);

        if (!kept)
                pool_push(o);        /* запас повний — назад у спільний пул */
}

/* ── пара колбеків ──────────────────────────────────────────────────── */
static enum cpuhp_state hp_state;
static bool fail_startup;            /* debugfs: наступний startup упаде один раз */

static int cache_cpu_online(unsigned int cpu)
{
        struct obj *batch = NULL, *o;
        struct cache *c;
        unsigned int have, need, i, n;

        /* потік cpuhp/N прибитий до свого ядра процесора, тож це законно */
        WARN_ON_ONCE(cpu != smp_processor_id());

        if (READ_ONCE(fail_startup)) {
                WRITE_ONCE(fail_startup, false);
                pr_info("startup  cpu=%u навмисно повертає -ENOMEM\n", cpu);
                return -ENOMEM;
        }

        local_lock(&cache.lock);
        have = this_cpu_ptr(&cache)->count;
        local_unlock(&cache.lock);

        /* НЕ «додати WANT», а «доповнити ДО WANT»: після відкоту цей колбек
         * приходить на копію, яку ніхто не спорожнив */
        need = (have < WANT) ? WANT - have : 0;

        for (i = 0; i < need; i++) {          /* виділяємо ДО замка: тут можна спати */
                o = kmalloc(sizeof(*o), GFP_KERNEL);
                if (!o) {
                        obj_list_free(batch); /* прибрати за собою й чесно впасти */
                        return -ENOMEM;
                }
                o->next = batch;
                batch = o;
        }

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        while (batch && c->count < WANT) {
                o = batch;
                batch = o->next;
                o->next = c->head;
                c->head = o;
                c->count++;
        }
        n = c->count;
        c->filled++;
        local_unlock(&cache.lock);

        obj_list_free(batch);                 /* зайве, якщо лишилося */
        pr_info("startup  cpu=%u count=%u (біжу на cpu%d)\n",
                cpu, n, smp_processor_id());
        return 0;
}

static int cache_cpu_offline(unsigned int cpu)
{
        struct obj *list, *o;
        struct cache *c;
        unsigned long n = 0;

        WARN_ON_ONCE(cpu != smp_processor_id());

        local_lock(&cache.lock);
        c = this_cpu_ptr(&cache);
        list = c->head;              /* забираємо весь список одним рухом */
        c->head = NULL;
        c->count = 0;
        local_unlock(&cache.lock);

        while (list) {               /* і аж потім, без замка, роздаємо в пул */
                o = list;
                list = o->next;
                pool_push(o);
                n++;
        }

        this_cpu_add(cache.drained, n);
        pr_info("teardown cpu=%u злито %lu, у пулі %lu\n",
                cpu, n, READ_ONCE(pool_size));
        return 0;                    /* teardown не має права не вдатися */
}

/* ── вітрина: підсумок за possible, а не за online ──────────────────── */
static int stats_show(struct seq_file *m, void *v)
{
        unsigned long hits = 0, misses = 0, drained = 0;
        unsigned int cpu;

        seq_puts(m, "cpu  online  count  hits  misses  filled  drained\n");
        for_each_possible_cpu(cpu) {
                struct cache *c = per_cpu_ptr(&cache, cpu);

                seq_printf(m, "%3u  %6d  %5u  %4lu  %6lu  %6lu  %7lu\n",
                           cpu, cpu_online(cpu), c->count,
                           c->hits, c->misses, c->filled, c->drained);
                hits += c->hits;
                misses += c->misses;
                drained += c->drained;
        }
        seq_printf(m, "разом: hits %lu, misses %lu, drained %lu, у пулі %lu\n",
                   hits, misses, drained, READ_ONCE(pool_size));
        return 0;
}
DEFINE_SHOW_ATTRIBUTE(stats);

static ssize_t churn_write(struct file *f, const char __user *ubuf,
                           size_t count, loff_t *ppos)
{
        unsigned int n, i;
        int ret = kstrtouint_from_user(ubuf, count, 10, &n);

        if (ret)
                return ret;

        for (i = 0; i < n; i++) {
                struct obj *o = obj_get();

                if (!o)
                        return -ENOMEM;
                obj_put(o);
        }
        return count;
}

static const struct file_operations churn_fops = {
        .owner  = THIS_MODULE,
        .write  = churn_write,
        .llseek = noop_llseek,
};

static struct dentry *dir;

static int __init cpucache_init(void)
{
        int ret;

        dir = debugfs_create_dir("cpucache", NULL);
        debugfs_create_file("stats", 0444, dir, NULL, &stats_fops);
        debugfs_create_file("churn", 0200, dir, NULL, &churn_fops);
        debugfs_create_bool("fail_startup", 0644, dir, &fail_startup);

        /* реєстрація — ОСТАННІМ рядком: вона одразу кличе startup
         * на всіх ядрах процесора, що вже онлайн */
        ret = cpuhp_setup_state(CPUHP_AP_ONLINE_DYN, "cpucache:online",
                                cache_cpu_online, cache_cpu_offline);
        if (ret < 0) {               /* саме < 0: динамічний номер додатний */
                debugfs_remove_recursive(dir);
                return ret;
        }
        hp_state = ret;
        pr_info("узято динамічний стан %d\n", hp_state);
        return 0;
}

static void __exit cpucache_exit(void)
{
        cpuhp_remove_state(hp_state);   /* ПЕРШИМ: зливає всі запаси в пул */
        debugfs_remove_recursive(dir);
        obj_list_free(pool_head);       /* і аж тепер звільняти пам'ять */
        pool_head = NULL;
        pool_size = 0;
        pr_info("вивантажено\n");
}

module_init(cpucache_init);
module_exit(cpucache_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Per-CPU запас об'єктів із парою колбеків cpuhp");
