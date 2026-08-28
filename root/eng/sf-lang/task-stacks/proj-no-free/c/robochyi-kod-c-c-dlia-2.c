void *pool_alloc(void)
{
    if (freeList == NULL)
        return NULL;              /* пул вичерпано — штатна ситуація */

    void *blk  = freeList;       /* знімаємо голову                 */
    freeList   = *(void **)blk;  /* голова → наступний вільний      */
    return blk;
}

void pool_free(void *p)
{
    if (p == NULL) return;

    *(void **)p = freeList;      /* у блок пишемо стару голову      */
    freeList    = p;             /* блок стає новою головою         */
}
