int   virtqueue_add_sgs(struct virtqueue *vq, struct scatterlist *sgs[],
                        unsigned int out_sgs, unsigned int in_sgs,
                        void *data, gfp_t gfp);
int   virtqueue_add_outbuf(struct virtqueue *vq, struct scatterlist sg[],
                           unsigned int num, void *data, gfp_t gfp);
int   virtqueue_add_inbuf(struct virtqueue *vq, struct scatterlist sg[],
                          unsigned int num, void *data, gfp_t gfp);
bool  virtqueue_kick(struct virtqueue *vq);
void *virtqueue_get_buf(struct virtqueue *vq, unsigned int *len);
void  virtqueue_disable_cb(struct virtqueue *vq);
bool  virtqueue_enable_cb(struct virtqueue *vq);
bool  virtqueue_enable_cb_delayed(struct virtqueue *vq);
