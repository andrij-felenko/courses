/* один запит: заголовок пристрій читає, сторінку — заповнює */
struct scatterlist hdr_sg, data_sg, *sgs[2];

sg_init_one(&hdr_sg,  &req->hdr, sizeof(req->hdr));
sg_init_one(&data_sg,  req->buf, PAGE_SIZE);
sgs[0] = &hdr_sg;    /* out */
sgs[1] = &data_sg;   /* in  */

if (virtqueue_add_sgs(vq, sgs, 1, 1, req, GFP_ATOMIC) == 0)
        virtqueue_kick(vq);

/* зворотний виклик черги — саме таким циклом, не інакше */
static void cb_recv(struct virtqueue *vq)
{
        struct my_req *req;
        unsigned int len;

        virtqueue_disable_cb(vq);
        do {
                while ((req = virtqueue_get_buf(vq, &len)) != NULL)
                        finish(req, len);
        } while (!virtqueue_enable_cb(vq));   /* false — поки гребли, приїхало ще */
}
