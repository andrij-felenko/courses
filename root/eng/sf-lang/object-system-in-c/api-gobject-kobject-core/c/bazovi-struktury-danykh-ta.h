/* Числовий ідентифікатор типу в системі GType (зазвичай uintptr_t) */
typedef gsize GType;

/* Заголовок будь-якого екземпляра об'єкта */
struct _GTypeInstance {
    GTypeClass *g_class;           /* Вказівник на структуру класу (vtable) */
};

/* Заголовок будь-якої структури класу (синглтона) */
struct _GTypeClass {
    GType g_type;                  /* Зворотне посилання на зареєстрований GType */
};

/* Базовий об'єкт GObject */
struct _GObject {
    GTypeInstance  g_type_instance;/* Зсув 0: вказівник на клас */
    volatile guint ref_count;      /* Атомарний лічильник посилань */
    GData         *qdata;          /* Асоціативний список довільних атрибутів */
};

/* Базовий клас GObjectClass */
struct _GObjectClass {
    GTypeClass   g_type_class;     /* Зсув 0: GType */
    
    /* Таблиця конструкторів та деструкторів */
    GObject*   (*constructor)     (GType type, guint n_props, GObjectConstructParam *props);
    void       (*set_property)    (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec);
    void       (*get_property)    (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec);
    void       (*dispose)         (GObject *object);   /* Розрив циклічних посилань */
    void       (*finalize)        (GObject *object);   /* Фінальне звільнення пам'яті */
    void       (*constructed)     (GObject *object);
};
