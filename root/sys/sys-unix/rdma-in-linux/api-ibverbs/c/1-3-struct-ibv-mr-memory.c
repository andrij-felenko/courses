// Реєстрація пам'яті у C
char *buffer = (char *)malloc(4096);
struct ibv_mr *mr = ibv_reg_mr(pd, buffer, 4096,
                               IBV_ACCESS_LOCAL_WRITE |
                               IBV_ACCESS_REMOTE_WRITE |
                               IBV_ACCESS_REMOTE_READ);
if (!mr) {
    perror("ibv_reg_mr failed");
}
// ...
ibv_dereg_mr(mr);
free(buffer);
