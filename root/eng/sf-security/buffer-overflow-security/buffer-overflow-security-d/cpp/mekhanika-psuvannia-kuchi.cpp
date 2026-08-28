// Концептуальна модель вилучення вузла в C++ з контролем цілісності покажчиків:
struct ChunkNode {
    ChunkNode* fd{nullptr};
    ChunkNode* bk{nullptr};
};

bool unlink_safe(ChunkNode* p) noexcept {
    if (!p || !p->fd || !p->bk) return false;
    // Перевірка цілісності: суміжний вузол повинен посилатися назад на поточний
    if (p->fd->bk != p || p->bk->fd != p) {
        return false; // Пошкодження зв'язного списку виявлено
    }
    p->fd->bk = p->bk;
    p->bk->fd = p->fd;
    return true;
}
