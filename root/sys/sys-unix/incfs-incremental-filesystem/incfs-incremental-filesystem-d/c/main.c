/* Виклик ioctl заповнення блоку мовою C */
struct incfs_fill_block block_data = {
    .block_index = 1,
    .data_len = 4096,
    .data = (uint64_t)(uintptr_t)user_buffer,
    .compression = 0
};

struct incfs_fill_blocks fill_args = {
    .count = 1,
    .fill_blocks = (uint64_t)(uintptr_t)&block_data
};

if (ioctl(incfs_file_fd, INCFS_IOC_FILL_BLOCKS, &fill_args) < 0) {
    perror("Помилка виконання INCFS_IOC_FILL_BLOCKS");
}
