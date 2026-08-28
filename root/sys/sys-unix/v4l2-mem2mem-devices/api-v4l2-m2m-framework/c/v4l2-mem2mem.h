#include <media/v4l2-mem2mem.h>

struct v4l2_m2m_ops {
    void (*device_run)(void *priv);
    int  (*job_ready)(void *priv);
    void (*job_abort)(void *priv);
};

/* Ініціалізація глобального диспетчера завдань пристрою M2M */
struct v4l2_m2m_dev *v4l2_m2m_init(const struct v4l2_m2m_ops *m2m_ops);

/* Звільнення ресурсів диспетчера під час вивантаження драйвера */
void v4l2_m2m_release(struct v4l2_m2m_dev *m2m_dev);

/* Створення контексту для відкритого файлового дескриптора */
struct v4l2_m2m_ctx *v4l2_m2m_ctx_init(
    struct v4l2_m2m_dev *m2m_dev,
    void *drv_priv,
    int (*queue_init)(void *priv, struct vb2_queue *src_vq, struct vb2_queue *dst_vq));

/* Знищення контексту при закритті дескриптора файлу */
void v4l2_m2m_ctx_release(struct v4l2_m2m_ctx *m2m_ctx);
