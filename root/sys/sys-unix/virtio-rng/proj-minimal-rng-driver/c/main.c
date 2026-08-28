// SPDX-License-Identifier: GPL-2.0
#include <linux/completion.h>
#include <linux/hw_random.h>
#include <linux/minmax.h>
#include <linux/module.h>
#include <linux/scatterlist.h>
#include <linux/slab.h>
#include <linux/virtio.h>
#include <linux/virtio_config.h>
#include <linux/virtio_ids.h>

/* Не менше за буфер, який просить каркас hw_random, і не менше за рядок кешу. */
#define KRNG_BUF  (SMP_CACHE_BYTES < 32 ? 32 : SMP_CACHE_BYTES)

struct krng {
	struct hwrng      hwrng;
	struct virtqueue *vq;
	struct completion filled;
	char              name[24];
	bool              registered;   /* чи дійшло до hwrng_register() */
	bool              gone;         /* пристрій відв'язують */
	unsigned int      avail;        /* скільки байтів приїхало */
	unsigned int      idx;          /* скільки з них уже роздано */
	u8               *buf;          /* окремий kmalloc: сюди пише пристрій */
};

/* Поставити буфер у чергу й сповістити господаря. Кличуть із probe і з тієї
   миті, коли буфер щойно спорожнів, — тобто завжди з контексту задачі. */
static void krng_arm(struct krng *vi)
{
	struct scatterlist sg;

	reinit_completion(&vi->filled);
	vi->avail = 0;
	vi->idx = 0;

	sg_init_one(&sg, vi->buf, KRNG_BUF);
	/* Черга розрахована на один буфер, і він у ній рівно один. */
	if (WARN_ON_ONCE(virtqueue_add_inbuf(vi->vq, &sg, 1, vi->buf,
					     GFP_KERNEL) < 0))
		return;
	virtqueue_kick(vi->vq);
}

/* Контекст переривання: тільки забрати буфер і розбудити читача. */
static void krng_done(struct virtqueue *vq)
{
	struct krng *vi = vq->vdev->priv;
	unsigned int len;

	/* Виклик може бути й чужим — лінія PCI буває спільною. */
	if (!virtqueue_get_buf(vq, &len))
		return;

	/* len приїхала від господаря: це вхідні дані, а не факт. Затискаємо
	   тут-таки, бо далі за нею беруть memcpy(). Публікація через release
	   не дає читачеві побачити нове avail раніше за самі байти. */
	smp_store_release(&vi->avail, min_t(unsigned int, len, KRNG_BUF));
	complete(&vi->filled);
}

/* Віддати шматок зі свого буфера; спорожнів — одразу поставити нове прохання. */
static unsigned int krng_drain(struct krng *vi, void *dst, size_t want)
{
	unsigned int n = min_t(unsigned int, want, vi->avail - vi->idx);

	memcpy(dst, vi->buf + vi->idx, n);
	vi->idx += n;
	if (vi->idx == vi->avail)
		krng_arm(vi);
	return n;
}

static int krng_read(struct hwrng *rng, void *dst, size_t want, bool wait)
{
	struct krng *vi = (struct krng *)rng->priv;
	size_t got = 0;
	int ret;

	if (vi->gone)
		return -ENODEV;

	if (smp_load_acquire(&vi->avail))       /* спершу те, що вже вдома */
		got = krng_drain(vi, dst, want);

	if (!wait)
		return got;

	while (got < want) {
		ret = wait_for_completion_killable(&vi->filled);
		if (ret < 0)
			return got ? got : ret;
		if (!smp_load_acquire(&vi->avail))
			return got;             /* розбудили не даними, а розбиранням */
		got += krng_drain(vi, dst + got, want - got);
	}
	return got;
}

/* Каркас просить припинити читання: той, хто спить у krng_read(), мусить вийти. */
static void krng_cleanup(struct hwrng *rng)
{
	complete(&((struct krng *)rng->priv)->filled);
}

static int krng_probe(struct virtio_device *vdev)
{
	struct krng *vi;
	int err;

	vi = kzalloc(sizeof(*vi), GFP_KERNEL);
	if (!vi)
		return -ENOMEM;

	/* Окремий kmalloc, а не поле структури: у цей буфер пише пристрій,
	   і він не має ділити рядок кешу з рештою полів. */
	vi->buf = kmalloc(KRNG_BUF, GFP_KERNEL);
	if (!vi->buf) {
		err = -ENOMEM;
		goto err_buf;
	}

	init_completion(&vi->filled);
	snprintf(vi->name, sizeof(vi->name), "krng.%d", vdev->index);

	vi->hwrng = (struct hwrng) {
		.name    = vi->name,
		.read    = krng_read,
		.cleanup = krng_cleanup,
		.priv    = (unsigned long)vi,
		/* .quality не ставимо: нуль означає «повна довіра, обмежена
		   стелею каркаса», а стеля від Linux 6.2 — 1024. */
	};
	vdev->priv = vi;

	vi->vq = virtio_find_single_vq(vdev, krng_done, "input");
	if (IS_ERR(vi->vq)) {
		err = PTR_ERR(vi->vq);
		goto err_vq;
	}

	/* ДО першого прохання, і саме в такому порядку. */
	virtio_device_ready(vdev);
	krng_arm(vi);
	return 0;

err_vq:
	kfree(vi->buf);
err_buf:
	kfree(vi);
	return err;
}

/* .scan ядро кличе після probe і після того, як пристрій позначено готовим, —
   тому перше читання від каркаса не потрапить у недобудований драйвер. */
static void krng_scan(struct virtio_device *vdev)
{
	struct krng *vi = vdev->priv;

	vi->registered = (hwrng_register(&vi->hwrng) == 0);
}

static void krng_remove(struct virtio_device *vdev)
{
	struct krng *vi = vdev->priv;

	/* Спершу назовні: доки джерело в каркасі, потік hwrng може ввійти
	   в krng_read() будь-якої миті. */
	vi->gone = true;
	vi->avail = 0;
	vi->idx = 0;
	complete(&vi->filled);
	if (vi->registered)
		hwrng_unregister(&vi->hwrng);

	/* Аж тепер розбираємо пристрій. */
	virtio_reset_device(vdev);
	vdev->config->del_vqs(vdev);
	kfree(vi->buf);
	kfree(vi);
}

static const struct virtio_device_id krng_id_table[] = {
	{ VIRTIO_ID_RNG, VIRTIO_DEV_ANY_ID },
	{ 0 },
};
MODULE_DEVICE_TABLE(virtio, krng_id_table);

static struct virtio_driver krng_driver = {
	.driver.name = KBUILD_MODNAME,
	.id_table    = krng_id_table,
	.probe       = krng_probe,
	.scan        = krng_scan,
	.remove      = krng_remove,
};
module_virtio_driver(krng_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Мінімальний драйвер virtio-rng");
