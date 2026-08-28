// SPDX-License-Identifier: GPL-2.0
#include <linux/devm-helpers.h>
#include <linux/fs.h>
#include <linux/i2c.h>
#include <linux/interrupt.h>
#include <linux/ktime.h>
#include <linux/math64.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/uaccess.h>
#include <linux/wait.h>
#include <linux/workqueue.h>

#define DVCH_REG_FIFO   0x02
#define DVCH_BURST      8     /* вибірок за одне переривання */
#define DVCH_SLOTS      4u    /* черга «потік → BH-робота» */
#define DVCH_RING       64u   /* степінь двійки: залишок замість ділення */
#define DVCH_LINE       48

struct dvch_sample {
	u64 ts;      /* наносекунди, зняті у верхній половині */
	s32 milli;   /* значення в тисячних */
};

struct dvch_raw {
	u64 ts;
	u8  b[DVCH_BURST * 2];
};

struct dvch {
	struct i2c_client *client;
	struct miscdevice  misc;

	/* Верхня половина → потік. Єдина передача в драйвері, що не є чергою:
	   ONESHOT не пускає другу верхню половину, доки потік не скінчився. */
	u64 stamp;

	struct work_struct bh_work;      /* softirq: розкодувати й опублікувати */
	struct work_struct stats_work;   /* kworker: звести під м'ютексом */

	/* Під спін-замком: сюди дотягується softirq. */
	spinlock_t         lock;
	struct dvch_raw    raw[DVCH_SLOTS];
	unsigned int       rhead, rtail;
	struct dvch_sample ring[DVCH_RING];
	unsigned int       head, tail;
	unsigned int       pack_n, pack_lost;
	s32                pack_min, pack_max;

	wait_queue_head_t  readers;

	/* Під м'ютексом: сюди дотягується лише контекст задачі. */
	struct mutex stats_lock;
	u64 total, lost;
	s32 all_min, all_max;
};

/* ─── верхня половина: апаратний контекст, сотні наносекунд ─────────────── */
static irqreturn_t dvch_hardirq(int irq, void *data)
{
	struct dvch *s = data;

	/* Спитати «чи наше це переривання» нема в кого: регістр стану лежить
	   за шиною. Тому лінія в цього давача мусить бути лише його.      */
	s->stamp = ktime_get_ns();
	return IRQ_WAKE_THREAD;
}

/* ─── потік переривання: контекст задачі, спати можна ───────────────────── */
static irqreturn_t dvch_thread(int irq, void *data)
{
	struct dvch *s = data;
	struct dvch_raw *slot;
	u8 buf[DVCH_BURST * 2];
	int ret;

	/* Саме це читання знімає запит із лінії — більше ніщо його не зніме. */
	ret = i2c_smbus_read_i2c_block_data(s->client, DVCH_REG_FIFO,
					    sizeof(buf), buf);
	if (ret != sizeof(buf)) {
		dev_warn_ratelimited(&s->client->dev, "шина відповіла %d\n", ret);
		return IRQ_HANDLED;   /* лінію однаково треба розмаскувати */
	}

	spin_lock_bh(&s->lock);       /* «_bh»: цей замок бере й BH-робота */
	if (s->rhead - s->rtail == DVCH_SLOTS) {
		s->rtail++;
		s->pack_lost += DVCH_BURST;
	}
	slot = &s->raw[s->rhead++ % DVCH_SLOTS];
	slot->ts = s->stamp;
	memcpy(slot->b, buf, sizeof(buf));
	spin_unlock_bh(&s->lock);

	queue_work(system_bh_wq, &s->bh_work);
	return IRQ_HANDLED;           /* звідси ядро розмаскує лінію */
}

/* ─── BH-робота: softirq; те, що колись було тасклетом ──────────────────── */
static void dvch_bh(struct work_struct *w)
{
	struct dvch *s = container_of(w, struct dvch, bh_work);
	bool published = false;

	/* Ми вже в softirq: тут беруть простий spin_lock — глушити нижні
	   половини нема від кого, вони і є ми.                          */
	spin_lock(&s->lock);
	while (s->rhead != s->rtail) {
		struct dvch_raw *slot = &s->raw[s->rtail++ % DVCH_SLOTS];
		int i;

		for (i = 0; i < DVCH_BURST; i++) {
			s16 code = (s16)(((u16)slot->b[2 * i] << 8) |
					 slot->b[2 * i + 1]);
			struct dvch_sample smp = {
				.ts    = slot->ts + i * 1000000ull,  /* 1 кГц */
				.milli = code * 1000 / 32,
			};

			if (s->head - s->tail == DVCH_RING) {
				s->tail++;      /* свіже цінніше за старе */
				s->pack_lost++;
			}
			s->ring[s->head++ % DVCH_RING] = smp;

			if (!s->pack_n || smp.milli < s->pack_min)
				s->pack_min = smp.milli;
			if (!s->pack_n || smp.milli > s->pack_max)
				s->pack_max = smp.milli;
			s->pack_n++;
		}
		published = true;
	}
	spin_unlock(&s->lock);

	if (published) {
		wake_up_interruptible(&s->readers);
		schedule_work(&s->stats_work);
	}
}

/* ─── робоча черга: kworker, спати можна ────────────────────────────────── */
static void dvch_stats(struct work_struct *w)
{
	struct dvch *s = container_of(w, struct dvch, stats_work);
	unsigned int n, lost;
	s32 lo, hi;

	spin_lock_bh(&s->lock);
	n = s->pack_n;      lost = s->pack_lost;
	lo = s->pack_min;   hi = s->pack_max;
	s->pack_n = 0;      s->pack_lost = 0;
	spin_unlock_bh(&s->lock);

	if (!n && !lost)
		return;

	mutex_lock(&s->stats_lock);
	if (n) {
		if (!s->total || lo < s->all_min)
			s->all_min = lo;
		if (!s->total || hi > s->all_max)
			s->all_max = hi;
		s->total += n;
	}
	s->lost += lost;
	mutex_unlock(&s->stats_lock);
}

/* ─── символьний пристрій ───────────────────────────────────────────────── */
static bool dvch_pop(struct dvch *s, struct dvch_sample *out)
{
	bool got = false;

	spin_lock_bh(&s->lock);
	if (s->head != s->tail) {
		*out = s->ring[s->tail++ % DVCH_RING];
		got = true;
	}
	spin_unlock_bh(&s->lock);
	return got;
}

static ssize_t dvch_read(struct file *f, char __user *ubuf,
			 size_t count, loff_t *ppos)
{
	struct dvch *s = container_of(f->private_data, struct dvch, misc);
	struct dvch_sample smp;
	char line[DVCH_LINE];
	u64 sec;
	u32 nsec;
	int len, ret;

	if (count < DVCH_LINE)
		return -EINVAL;        /* рядок цілий або жодного */

	if (!dvch_pop(s, &smp)) {
		if (f->f_flags & O_NONBLOCK)
			return -EAGAIN;
		ret = wait_event_interruptible(s->readers, dvch_pop(s, &smp));
		if (ret)
			return ret;    /* -ERESTARTSYS: прийшов сигнал */
	}

	sec = div_u64_rem(smp.ts, NSEC_PER_SEC, &nsec);
	len = scnprintf(line, sizeof line, "%llu.%09u %d\n", sec, nsec, smp.milli);
	if (copy_to_user(ubuf, line, len))
		return -EFAULT;
	return len;
}

static int dvch_open(struct inode *ino, struct file *f)
{
	return stream_open(ino, f);    /* позиції в потоці немає */
}

static const struct file_operations dvch_fops = {
	.owner = THIS_MODULE,
	.open  = dvch_open,
	.read  = dvch_read,
};

static ssize_t stats_show(struct device *dev, struct device_attribute *a,
			  char *buf)
{
	struct dvch *s = i2c_get_clientdata(to_i2c_client(dev));
	ssize_t n;

	mutex_lock(&s->stats_lock);
	n = sysfs_emit(buf, "усього %llu, викинуто %llu, від %d до %d\n",
		       s->total, s->lost, s->all_min, s->all_max);
	mutex_unlock(&s->stats_lock);
	return n;
}
static DEVICE_ATTR_RO(stats);

static struct attribute *dvch_attrs[] = { &dev_attr_stats.attr, NULL };
ATTRIBUTE_GROUPS(dvch);

/* ─── прив'язка й відв'язка ─────────────────────────────────────────────── */
static int dvch_probe(struct i2c_client *client)
{
	struct device *dev = &client->dev;
	struct dvch *s;
	int ret;

	if (client->irq <= 0)
		return dev_err_probe(dev, -EINVAL, "потрібна лінія переривання\n");

	s = devm_kzalloc(dev, sizeof(*s), GFP_KERNEL);
	if (!s)
		return -ENOMEM;

	s->client = client;
	spin_lock_init(&s->lock);
	mutex_init(&s->stats_lock);
	init_waitqueue_head(&s->readers);
	i2c_set_clientdata(client, s);

	/* devm розбирає в ЗВОРОТНОМУ порядку — отже, реєструємо ланцюжок
	   з хвоста до голови: скасувати споживача раніше за постачальника
	   означає дати постачальникові поставити роботу після скасування. */
	ret = devm_work_autocancel(dev, &s->stats_work, dvch_stats);
	if (ret)
		return ret;
	ret = devm_work_autocancel(dev, &s->bh_work, dvch_bh);
	if (ret)
		return ret;

	ret = devm_request_threaded_irq(dev, client->irq,
					dvch_hardirq, dvch_thread,
					IRQF_ONESHOT, "davach", s);
	if (ret)
		return dev_err_probe(dev, ret, "переривання %d зайняте\n",
				     client->irq);

	s->misc.minor  = MISC_DYNAMIC_MINOR;
	s->misc.name   = "davach";
	s->misc.fops   = &dvch_fops;
	s->misc.parent = dev;

	return misc_register(&s->misc);   /* останній рядок: тепер нас видно */
}

static void dvch_remove(struct i2c_client *client)
{
	struct dvch *s = i2c_get_clientdata(client);

	misc_deregister(&s->misc);
	/* Далі devm сам, проти течії: free_irq (він же дочекається потоку),
	   cancel_work_sync(bh_work), cancel_work_sync(stats_work), kfree(s). */
}

static const struct i2c_device_id dvch_id[] = { { "davach" }, { } };
MODULE_DEVICE_TABLE(i2c, dvch_id);

static const struct of_device_id dvch_of[] = {
	{ .compatible = "kurs,davach" },
	{ }
};
MODULE_DEVICE_TABLE(of, dvch_of);

static struct i2c_driver dvch_driver = {
	.driver = {
		.name           = "davach",
		.of_match_table = dvch_of,
		.dev_groups     = dvch_groups,
	},
	.probe    = dvch_probe,
	.remove   = dvch_remove,
	.id_table = dvch_id,
};
module_i2c_driver(dvch_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Давач I2C із трьома нижніми половинами");
