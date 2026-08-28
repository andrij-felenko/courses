// 1. Створення тимчасового файла та запис у C++20 через std::filesystem
std::filesystem::path temp_path = "/usr/bin/nginx.dpkg-new";
std::filesystem::path target_path = "/usr/bin/nginx";

{
    std::ofstream out(temp_path, std::ios::binary);
    out.write(payload_buffer, payload_len);
    out.flush();
}

// 2. Примусовий скид буферів (fsync) та атомарне перейменування
int fd = ::open(temp_path.c_str(), O_RDWR);
if (fd >= 0) {
    ::fsync(fd);
    ::close(fd);
}
std::filesystem::rename(temp_path, target_path);
