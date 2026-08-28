static int linear_map(struct dm_target *ti, struct bio *bio)
{
        struct linear_c *lc = ti->private;

        bio_set_dev(bio, lc->dev->bdev);
        bio->bi_iter.bi_sector =
                lc->start + dm_target_offset(ti, bio->bi_iter.bi_sector);

        return DM_MAPIO_REMAPPED;
}
