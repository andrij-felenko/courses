#include <iostream>
#include <string_view>
#include <system_error>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>

struct SharedRegion {
    pthread_mutex_t lock;
    int counter{0};
};

void init_shared_service_cpp(std::string_view shm_name, size_t size) {
    const std::string name_str(shm_name);

    // 1. Створення сегмента пам'яті
    int fd = ::shm_open(name_str.c_str(), O_CREAT | O_RDWR | O_EXCL, 0600);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), "shm_open failed");
    }

    // Охоронець 1: видалення імені сегмента з системи
    auto unlink_guard = make_scope_guard([&name_str] noexcept {
        ::shm_unlink(name_str.c_str());
    });

    // Охоронець 2: закриття файлового дескриптора на виході
    auto close_guard = make_scope_guard([fd] noexcept {
        ::close(fd);
    });

    // 2. Встановлення розміру
    if (::ftruncate(fd, static_cast<off_t>(size)) != 0) {
        throw std::system_error(errno, std::generic_category(), "ftruncate failed");
    }

    // 3. Відображення в адресний простір
    void* raw_ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (raw_ptr == MAP_FAILED) {
        throw std::system_error(errno, std::generic_category(), "mmap failed");
    }
    auto* region = static_cast<SharedRegion*>(raw_ptr);

    // Охоронець 3: скидання відображення у разі збою ініціалізації м'ютекса
    auto unmap_guard = make_scope_guard([raw_ptr, size] noexcept {
        ::munmap(raw_ptr, size);
    });

    // 4. Налаштування міжпроцесного м'ютекса
    pthread_mutexattr_t mattr;
    ::pthread_mutexattr_init(&mattr);
    auto mattr_guard = make_scope_guard([&mattr] noexcept {
        ::pthread_mutexattr_destroy(&mattr);
    });

    if (::pthread_mutexattr_setpshared(&mattr, PTHREAD_PROCESS_SHARED) != 0 ||
        ::pthread_mutex_init(&region->lock, &mattr) != 0) {
        throw std::system_error(errno, std::generic_category(), "mutex init failed");
    }

    region->counter = 0;

    // Успіх: сегмент ініціалізовано. Відв'язуємо охоронці, які знищували б створене середовище:
    unlink_guard.dismiss();
    unmap_guard.dismiss();
    // close_guard спрацює в кінці функції за планом, бо дескриптор після mmap більше не потрібен
    // mattr_guard спрацює в кінці функції, звільнивши атрибути м'ютекса
}
