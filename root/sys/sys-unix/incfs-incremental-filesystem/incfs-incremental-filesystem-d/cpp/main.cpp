// Виклик ioctl заповнення блоку мовою C++20
IncfsFillBlock block_data{
    .block_index = 1,
    .data_len = 4096,
    .data = reinterpret_cast<uint64_t>(user_buffer.data())
};

IncfsFillBlocks fill_args{
    .count = 1,
    .fill_blocks = reinterpret_cast<uint64_t>(&block_data)
};

if (::ioctl(incfs_file_fd, INCFS_IOC_FILL_BLOCKS, &fill_args) < 0) {
    std::cerr << "Помилка виконання INCFS_IOC_FILL_BLOCKS: " 
              << std::generic_category().message(errno) << '\n';
}
