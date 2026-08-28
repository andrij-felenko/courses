#define SG_CHAIN	0x01UL   /* біт 0: у page_link не сторінка, а покажчик
                                    на наступну пачку записів */
#define SG_END		0x02UL   /* біт 1: цей запис — останній у списку */

static inline struct scatterlist *sg_next(struct scatterlist *sg)
{
	if (sg_is_last(sg))
		return NULL;
	sg++;
	if (unlikely(sg_is_chain(sg)))
		sg = sg_chain_ptr(sg);
	return sg;
}
