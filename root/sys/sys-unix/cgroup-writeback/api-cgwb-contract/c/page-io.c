/* fs/ext4/page-io.c, спрощено */
static void io_submit_init_bio(struct ext4_io_submit *io, struct buffer_head *bh)
{
    struct bio *bio = bio_alloc(bh->b_bdev, BIO_MAX_VECS, REQ_OP_WRITE, GFP_NOIO);

    bio->bi_iter.bi_sector = bh->b_blocknr * (bh->b_size >> 9);
    bio->bi_end_io = ext4_end_bio;
    io->io_bio = bio;
    wbc_init_bio(io->io_wbc, bio);          /* пристрій уже відомий */
}

static void io_submit_add_bh(struct ext4_io_submit *io, struct inode *inode,
                             struct folio *folio, struct folio *io_folio,
                             struct buffer_head *bh)
{
    if (io->io_bio == NULL)
        io_submit_init_bio(io, bh);

    if (!bio_add_folio(io->io_bio, io_folio, bh->b_size, bh_offset(bh)))
        goto submit_and_retry;              /* bio повний — подати й почати новий */

    wbc_account_cgroup_owner(io->io_wbc, folio, bh->b_size);
}
