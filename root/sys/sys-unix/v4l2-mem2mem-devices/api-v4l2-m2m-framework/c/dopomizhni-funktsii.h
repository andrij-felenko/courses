/* Отримання покажчика на наступний готовий буфер у черзі */
struct vb2_v4l2_buffer *v4l2_m2m_next_src_buf(struct v4l2_m2m_ctx *m2m_ctx);
struct vb2_v4l2_buffer *v4l2_m2m_next_dst_buf(struct v4l2_m2m_ctx *m2m_ctx);

/* Вилучення буфера зі списку очікування (перехід у стан обробки апаратурою) */
struct vb2_v4l2_buffer *v4l2_m2m_src_buf_remove(struct v4l2_m2m_ctx *m2m_ctx);
struct vb2_v4l2_buffer *v4l2_m2m_dst_buf_remove(struct v4l2_m2m_ctx *m2m_ctx);

/* Перенесення метаданих (часова мітка, flags, timecode) між буферами */
void v4l2_m2m_buf_copy_metadata(const struct vb2_v4l2_buffer *out_vb,
                                struct vb2_v4l2_buffer *cap_vb,
                                bool copy_frame_types);

/* Завершення обробки буфера в ISR/Tasklet */
void v4l2_m2m_buf_done(struct vb2_v4l2_buffer *vbuf, enum vb2_buffer_state state);

/* Фіналізація поточного завдання та запуск наступного */
void v4l2_m2m_job_finish(struct v4l2_m2m_dev *m2m_dev, struct v4l2_m2m_ctx *m2m_ctx);
