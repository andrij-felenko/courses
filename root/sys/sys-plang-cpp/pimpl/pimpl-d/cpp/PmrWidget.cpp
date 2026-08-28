// PmrWidget.cpp
#include "PmrWidget.h"

struct PmrWidget::Impl {
    int data_[1024];
};

void PmrWidget::PmrDeleter::operator()(Impl* ptr) const noexcept {
    if (ptr) {
        ptr->~Impl();
        mr_->deallocate(ptr, sizeof(Impl), alignof(Impl));
    }
}

PmrWidget::PmrWidget(std::pmr::memory_resource* mr) {
    void* mem = mr->allocate(sizeof(Impl), alignof(Impl));
    auto* impl = ::new (mem) Impl();
    pImpl_ = std::unique_ptr<Impl, PmrDeleter>(impl, PmrDeleter{mr});
}

PmrWidget::~PmrWidget() = default;
