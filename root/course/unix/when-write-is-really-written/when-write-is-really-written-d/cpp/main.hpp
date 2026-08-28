// 1. Запис і скидання вмісту файлу через RAII-дескриптор
{
    UniqueFd fd(::open("/etc/app/config.json.tmp", O_WRONLY | O_CREAT | O_TRUNC, 0644));
    ::write(fd.get(), data.data(), data.size());
    ::fsync(fd.get());
}

// 2. Атомарне перейменування у цільове ім'я
std::filesystem::rename("/etc/app/config.json.tmp", "/etc/app/config.json");

// 3. Обов'язкова синхронізація дескриптора батьківського каталогу
{
    UniqueFd dir_fd(::open("/etc/app", O_RDONLY | O_DIRECTORY));
    ::fsync(dir_fd.get());
}
