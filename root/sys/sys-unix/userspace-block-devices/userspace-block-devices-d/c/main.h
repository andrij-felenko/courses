struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);                  /* прокинулися: якийсь тег готовий */

unsigned tag = (unsigned)cqe->user_data;
const struct ublksrv_io_desc *iod = &desc_area[tag];   /* спільна пам'ять, без виклику */

int res = serve(iod, buf[tag]);   /* наш код: хмара, розшифрування, дедуплікація — будь-що */

struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
struct ublksrv_io_cmd *cmd = (struct ublksrv_io_cmd *)sqe->cmd;
io_uring_prep_read(sqe, ublkc_fd, NULL, 0, 0);   /* обнуляємо поля, далі перекриваємо */
sqe->opcode  = IORING_OP_URING_CMD;
sqe->cmd_op  = UBLK_U_IO_COMMIT_AND_FETCH_REQ;
cmd->q_id    = q_id;
cmd->tag     = tag;
cmd->result  = res;              /* < 0 — помилка, інакше кількість оброблених байтів */
cmd->addr    = (__u64)(uintptr_t)buf[tag];
io_uring_submit(&ring);
