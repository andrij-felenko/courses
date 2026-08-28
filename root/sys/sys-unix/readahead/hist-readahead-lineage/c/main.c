/*
 * Read in the block, like bread, but also start I/O on the
 * read-ahead block (which is not allocated to the caller)
 */
breada(adev, blkno, rablkno)
{
    ...
    if (rablkno && !incore(dev, rablkno)) {
        rabp = getblk(dev, rablkno);
        if (rabp->b_flags & B_DONE)
            brelse(rabp);
        else {
            rabp->b_flags =| B_READ|B_ASYNC;
            rabp->b_wcount = -256;
            (*bdevsw[adev.d_major].d_strategy)(rabp);
        }
    }
    if (rbp==0)
        return(bread(dev, blkno));
    iowait(rbp);
    return(rbp);
}
