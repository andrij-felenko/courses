/* drivers/virtio/virtio_balloon.c */
static unsigned long virtio_balloon_shrinker_scan(struct shrinker *shrinker,
                                                 struct shrink_control *sc)
{
    struct virtio_balloon *vb = shrinker->private_data;

    /* Ядро вимагає вивільнити sc->nr_to_scan сторінок для порятунку від OOM */
    unsigned long freed = leak_balloon(vb, sc->nr_to_scan);

    /* Оновлюємо лічильники й сповіщаємо хост */
    update_balloon_size(vb);
    return freed ? freed : SHRINK_STOP;
}

static unsigned long virtio_balloon_shrinker_count(struct shrinker *shrinker,
                                                  struct shrink_control *sc)
{
    struct virtio_balloon *vb = shrinker->private_data;

    /* Повідомляємо підсистемі MM, скільки сторінок утримує балон */
    return vb->num_pages;
}
