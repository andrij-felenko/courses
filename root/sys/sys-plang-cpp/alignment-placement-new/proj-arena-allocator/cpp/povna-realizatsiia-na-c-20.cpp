#include <iostream>
#include <memory>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>
#include <type_traits>
#include <utility>
#include <stdexcept>
#include <new>

class MonotonicArena {
public:
    // Конструктор виділяє сирий буфер потрібного розміру з фундаментальним вирівнюванням
    explicit MonotonicArena(std::size_t capacity)
        : capacity_(capacity),
          space_left_(capacity),
          cleanup_head_(nullptr) {
        // Виділяємо сиру пам'ять через operator new з максимальним скалярним вирівнюванням
        buffer_ = static_cast<std::byte*>(
            ::operator new(capacity_, std::align_val_t(alignof(std::max_align_t)))
        );
        current_ptr_ = buffer_;
    }

    // Забороняємо копіювання, щоб уникнути подвійного виклику деструкторів об'єктів
    MonotonicArena(const MonotonicArena&) = delete;
    MonotonicArena& operator=(const MonotonicArena&) = delete;

    // Дозволяємо переміщення арени (Move Semantics)
    MonotonicArena(MonotonicArena&& other) noexcept
        : buffer_(other.buffer_),
          capacity_(other.capacity_),
          current_ptr_(other.current_ptr_),
          space_left_(other.space_left_),
          cleanup_head_(other.cleanup_head_) {
        other.buffer_ = nullptr;
        other.capacity_ = 0;
        other.current_ptr_ = nullptr;
        other.space_left_ = 0;
        other.cleanup_head_ = nullptr;
    }

    MonotonicArena& operator=(MonotonicArena&& other) noexcept {
        if (this != &other) {
            destroy_all();
            if (buffer_) {
                ::operator delete(buffer_, std::align_val_t(alignof(std::max_align_t)));
            }
            buffer_ = other.buffer_;
            capacity_ = other.capacity_;
            current_ptr_ = other.current_ptr_;
            space_left_ = other.space_left_;
            cleanup_head_ = other.cleanup_head_;

            other.buffer_ = nullptr;
            other.capacity_ = 0;
            other.current_ptr_ = nullptr;
            other.space_left_ = 0;
            other.cleanup_head_ = nullptr;
        }
        return *this;
    }

    // Деструктор арени викликає всі деструктори створених об'єктів та звільняє буфер
    ~MonotonicArena() {
        if (buffer_) {
            destroy_all();
            ::operator delete(buffer_, std::align_val_t(alignof(std::max_align_t)));
        }
    }

    // 1. Сире виділення пам'яті під байти із заданим вирівнюванням
    void* allocate_raw(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t)) {
        void* ptr = current_ptr_;
        std::size_t space = space_left_;

        // std::align знаходить першу адресу, кратну alignment, всередині доступного простору
        void* aligned = std::align(alignment, bytes, ptr, space);
        if (!aligned) {
            throw std::bad_alloc();
        }

        // Обчислюємо, скільки всього байтів (разом із padding) було спожито
        std::size_t consumed = (static_cast<std::byte*>(aligned) - current_ptr_) + bytes;
        current_ptr_ = static_cast<std::byte*>(aligned) + bytes;
        space_left_ -= consumed;

        return aligned;
    }

    // 2. Створення об'єкта через розміщувальний new
    template <typename T, typename... Args>
    T* emplace(Args&&... args) {
        // Зберігаємо поточний стан на випадок винятку в конструкторі для відкату
        std::byte* prev_ptr = current_ptr_;
        std::size_t prev_space = space_left_;

        // Виділяємо правильно вирівняну ділянку пам'яті під T
        void* storage = allocate_raw(sizeof(T), alignof(T));

        T* object = nullptr;
        try {
            // Викликаємо неалокуючий розміщувальний new
            object = ::new (storage) T(std::forward<Args>(args)...);
        } catch (...) {
            // Відкат стану алокатора, якщо конструктор кинув виняток
            current_ptr_ = prev_ptr;
            space_left_ = prev_space;
            throw;
        }

        // Якщо тип має нетривіальний деструктор, додаємо вузол у список очищення
        if constexpr (!std::is_trivially_destructible_v<T>) {
            register_destructor(object);
        }

        return object;
    }

    // Скидання арени без повторного виділення буфера
    void reset() {
        destroy_all();
        current_ptr_ = buffer_;
        space_left_ = capacity_;
    }

    [[nodiscard]] std::size_t bytes_used() const noexcept {
        return capacity_ - space_left_;
    }

    [[nodiscard]] std::size_t space_left() const noexcept {
        return space_left_;
    }

private:
    // Структура для збереження адреси об'єкта та покажчика на функцію його руйнування
    struct CleanupNode {
        void (*destructor_fn)(void*);
        void* object_ptr;
        CleanupNode* next;
    };

    template <typename T>
    void register_destructor(T* obj) {
        // Виділяємо пам'ять під сам вузол очищення всередині цієї ж арени
        void* node_storage = allocate_raw(sizeof(CleanupNode), alignof(CleanupNode));
        
        auto* node = ::new (node_storage) CleanupNode{
            [](void* ptr) noexcept {
                static_cast<T*>(ptr)->~T(); // явний виклик деструктора потрібного типу
            },
            obj,
            cleanup_head_
        };
        cleanup_head_ = node;
    }

    // Виклик деструкторів у зворотній послідовності (LIFO)
    void destroy_all() noexcept {
        CleanupNode* current = cleanup_head_;
        while (current != nullptr) {
            current->destructor_fn(current->object_ptr);
            current = current->next;
        }
        cleanup_head_ = nullptr;
    }

    std::byte* buffer_{nullptr};
    std::size_t capacity_{0};
    std::byte* current_ptr_{nullptr};
    std::size_t space_left_{0};
    CleanupNode* cleanup_head_{nullptr};
};
