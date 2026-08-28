#include <cstdint>
#include <memory>
#include <system_error>
#include <span>

using PageId = uint32_t;

enum class BTreeErrorCode {
    Success = 0,
    PageNotFound,
    BufferPoolFull,
    DiskReadError,
    DiskWriteError,
    PageCorrupted,
    KeyAlreadyExists,
    KeyNotFound
};

class BTreeException : public std::runtime_error {
public:
    explicit BTreeException(BTreeErrorCode code, const std::string& msg)
        : std::runtime_error(msg), code_(code) {}
    [[nodiscard]] BTreeErrorCode code() const noexcept { return code_; }
private:
    BTreeErrorCode code_;
};

/* Інтерфейс утримання сторінки у пам'яті (RAII Page Handle) */
class PageHandle {
public:
    virtual ~PageHandle() = default;

    /* Отримати прямий вказівник на 4KB байтовий буфер */
    [[nodiscard]] virtual std::span<uint8_t, PAGE_SIZE> data() noexcept = 0;
    [[nodiscard]] virtual std::span<const uint8_t, PAGE_SIZE> data() const noexcept = 0;

    /* Позначити сторінку як брудну (підлягає запису на диск) */
    virtual void mark_dirty() noexcept = 0;

    /* Отримати ідентифікатор сторінки */
    [[nodiscard]] virtual PageId page_id() const noexcept = 0;
};

/* Головний контракт інтерфейсу BufferPoolManager */
class IBufferPoolManager {
public:
    virtual ~IBufferPoolManager() = default;

    /* Завантажити сторінку з диска або отримати з клейму кешу */
    [[nodiscard]] virtual std::unique_ptr<PageHandle> fetch_page(PageId page_id) = 0;

    /* Створити нову дискову сторінку */
    [[nodiscard]] virtual std::unique_ptr<PageHandle> new_page(PageId* out_page_id) = 0;

    /* Вивільнити сторінку (зменшити лічильник pin_count) */
    virtual void unpin_page(PageId page_id, bool is_dirty) = 0;

    /* Примусово скинути сторінку на диск (FSYNC) */
    virtual void flush_page(PageId page_id) = 0;

    /* Скинути всі брудні сторінки індексу */
    virtual void flush_all_pages() = 0;
};
