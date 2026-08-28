    Shared(Shared&& o) noexcept : cb_(o.cb_) { o.cb_ = nullptr; }

    Shared& operator=(Shared&& o) noexcept {
        if (this != &o) {
            if (cb_) cb_->release();          // звільнити своє старе
            cb_ = o.cb_;                       // вкрасти чуже
            o.cb_ = nullptr;                   // джерело спорожніти
        }
        return *this;
    }
