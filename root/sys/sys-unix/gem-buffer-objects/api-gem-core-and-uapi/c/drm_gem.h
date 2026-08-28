/* include/drm/drm_gem.h */
struct drm_gem_object_funcs {
    /** Звільнення специфічних для драйвера ресурсів при видаленні */
    void (*free)(struct drm_gem_object *obj);

    /** Викликається, коли процес створює новий числовий хендл */
    int (*open)(struct drm_gem_object *obj, struct drm_file *file);

    /** Викликається, коли процес закриває числовий хендл */
    void (*close)(struct drm_gem_object *obj, struct drm_file *file);

    /** Друк діагностичної інформації в debugfs */
    void (*print_info)(struct drm_printer *p, unsigned int indent,
                       const struct drm_gem_object *obj);

    /** Налаштування відображення сторінок VMA при виклику mmap */
    int (*mmap)(struct drm_gem_object *obj, struct vm_area_struct *vma);

    /** Створення scatter-gather таблиці для DMA передачі */
    struct sg_table *(*get_sg_table)(struct drm_gem_object *obj);

    /** Відображення буфера в безперервний простір ядра vmalloc */
    int (*vmap)(struct drm_gem_object *obj, struct iosys_map *map);

    /** Скасування відображення з адресного простору ядра */
    void (*vunmap)(struct drm_gem_object *obj, struct iosys_map *map);

    /** Фіксація фізичних сторінок у пам'яті (заборона витіснення) */
    int (*pin)(struct drm_gem_object *obj);

    /** Дозвіл на витіснення або переміщення сторінок */
    void (*unpin)(struct drm_gem_object *obj);
};
