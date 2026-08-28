/* Спрощена логіка швидкого шляху маршрутизації у ядрі Linux */
blk_qc_t nvme_ns_head_submit_bio(struct bio *bio)
{
    struct nvme_ns_head *head = bio->bi_bdev->bd_disk->private_data;
    struct nvme_ns *ns;
    
    /* 1. Критична секція RCU: пошук працездатного шляху без блокувань */
    rcu_read_lock();
    ns = nvme_find_path(head);
    if (likely(ns)) {
        /* 2. Підміна цільового пристрою безпосередньо у вхідному bio */
        bio_set_dev(bio, ns->disk->part0);
        bio->bi_opf |= REQ_NVME_MPATH;
        rcu_read_unlock();
        
        /* 3. Пряме передавання запиту в апаратну чергу вибраного контролера */
        return submit_bio_noacache(bio);
    }
    rcu_read_unlock();
    
    /* 4. Якщо всі шляхи недоступні — запит ставиться у чергу повтору */
    return nvme_mpath_requeue_bio(head, bio);
}
