/* include/drm/drm_gem.h */
struct drm_gem_object {
    /** @refcount: Атомарний лічильник посилань ядра */
    struct kref refcount;

    /** @handle_count: Кількість відкритих числових дескрипторів у процесах */
    unsigned handle_count;

    /** @dev: Вказівник на батьківський графічний пристрій DRM */
    struct drm_device *dev;

    /** @filp: Анонімний файл tmpfs/shmem для виділення сторінок пам'яті */
    struct file *filp;

    /** @vma_node: Вузол дерева менеджера фальшивих зміщень mmap */
    struct drm_vma_offset_node vma_node;

    /** @size: Розмір буфера в байтах, вирівняний за межею PAGE_SIZE */
    size_t size;

    /** @funcs: Таблиця віртуальних методів драйвера для цього об'єкта */
    const struct drm_gem_object_funcs *funcs;

    /** @dma_buf: Прив'язаний експортований dma-buf або NULL */
    struct dma_buf *dma_buf;

    /** @import_attach: Вкладення при імпорті буфера з іншого драйвера */
    struct dma_buf_attachment *import_attach;

    /** @resv: Вказівник на об'єкт резервації та огорож синхронізації */
    struct dma_resv *resv;

    /** @_resv: Вбудований локальний об'єкт резервації за замовчуванням */
    struct dma_resv _resv;
};
