#include "budget/fragment_resource.hpp"

#include <algorithm>
#include <bit>
#include <cstdint>
#include <new>
#include <stdexcept>

namespace budget {

FragmentAwareResource::FragmentAwareResource(std::span<std::byte> arena)
{
    const auto raw     = std::bit_cast<std::uintptr_t>(arena.data());
    const auto aligned = static_cast<std::uintptr_t>(align_up(raw));
    const auto skew    = static_cast<std::size_t>(aligned - raw);

    if (arena.size() <= skew + header_size() + kAlign) {
        throw std::invalid_argument{"арена замала навіть під один блок"};
    }

    std::byte* start = arena.data() + skew;
    const std::size_t usable = arena.size() - skew - header_size();

    head_ = ::new (static_cast<void*>(start)) Block{nullptr, nullptr, usable, false};
    capacity_ = usable;
}

bool FragmentAwareResource::owns(const Block* block) const noexcept
{
    for (const Block* b = head_; b != nullptr; b = b->next) {
        if (b == block) {
            return true;
        }
    }
    return false;
}

void* FragmentAwareResource::do_allocate(std::size_t bytes, std::size_t alignment)
{
    // Кожен блок починається на межі max_align_t; суворіше вирівнювання
    // потребувало б окремого поля зсуву й тут свідомо не підтримується.
    if (alignment > kAlign) {
        ++failures_;
        throw std::bad_alloc{};
    }

    const std::size_t need = align_up(bytes == 0 ? 1 : bytes);

    for (Block* b = head_; b != nullptr; b = b->next) {
        if (b->used || b->size < need) {
            continue;
        }

        // Хвіст відрізаємо лише тоді, коли з нього вийде корисний блок.
        if (b->size >= need + header_size() + kAlign) {
            auto* tail_addr =
                std::bit_cast<std::byte*>(b) + header_size() + need;
            Block* tail = ::new (static_cast<void*>(tail_addr))
                Block{b->next, b, b->size - need - header_size(), false};

            if (tail->next != nullptr) {
                tail->next->prev = tail;
            }
            b->next = tail;
            b->size = need;
        }

        b->used = true;
        used_ += b->size;
        return std::bit_cast<std::byte*>(b) + header_size();
    }

    ++failures_;
    throw std::bad_alloc{};
}

void FragmentAwareResource::do_deallocate(void* ptr, std::size_t /*bytes*/,
                                          std::size_t /*alignment*/) noexcept
{
    if (ptr == nullptr) {
        return;
    }

    auto* block = std::bit_cast<Block*>(static_cast<std::byte*>(ptr) -
                                        header_size());
    if (!owns(block) || !block->used) {
        return; // чужий або вже звільнений вказівник не має рвати список
    }

    block->used = false;
    used_ -= block->size;

    // Склеювання із сусідами — єдине, що стримує ріст фрагментації.
    if (Block* next = block->next; next != nullptr && !next->used) {
        block->size += header_size() + next->size;
        block->next = next->next;
        if (block->next != nullptr) {
            block->next->prev = block;
        }
    }
    if (Block* prev = block->prev; prev != nullptr && !prev->used) {
        prev->size += header_size() + block->size;
        prev->next = block->next;
        if (prev->next != nullptr) {
            prev->next->prev = prev;
        }
    }
}

bool FragmentAwareResource::do_is_equal(
    const std::pmr::memory_resource& other) const noexcept
{
    // Пам'ять цієї арени вміє звільняти лише вона сама.
    return this == &other;
}

FragmentAwareResource::Stats FragmentAwareResource::stats() const noexcept
{
    Stats s;
    s.capacity = capacity_;
    s.used     = used_;
    s.failures = failures_;

    for (const Block* b = head_; b != nullptr; b = b->next) {
        if (b->used) {
            continue;
        }
        s.free_total += b->size;
        ++s.free_blocks;
        s.largest_free = std::max(s.largest_free, b->size);
    }

    if (s.free_total > 0) {
        s.fragmentation = 1.0 - static_cast<double>(s.largest_free) /
                                    static_cast<double>(s.free_total);
    }
    return s;
}

Budget FragmentAwareResource::audit(std::size_t min_free_bytes,
                                    std::size_t min_largest_bytes) const noexcept
{
    const Stats s = stats();

    Budget flags = Budget::None;
    if (s.free_total < min_free_bytes) {
        flags |= Budget::HeapLow;
    }
    // Вільного може вистачати з надлишком, але якщо найбільший суцільний блок
    // менший за найтовстіший буфер, наступне виділення однаково впаде.
    if (s.largest_free < min_largest_bytes) {
        flags |= Budget::HeapFragmented;
    }
    return flags;
}

} // namespace budget
