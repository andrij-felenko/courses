struct media_v2_topology {
    __u64 topology_version; /* Монотонний лічильник версії топології в ядрі */
    __u32 num_entities;     /* Кількість знайдених entities */
    __u32 reserved1;
    __u64 ptr_entities;     /* Вказівник на масив struct media_v2_entity */
    __u32 num_interfaces;   /* Кількість системних інтерфейсів */
    __u32 reserved2;
    __u64 ptr_interfaces;   /* Вказівник на масив struct media_v2_interface */
    __u32 num_pads;         /* Кількість контактних майданчиків (pads) */
    __u32 reserved3;
    __u64 ptr_pads;         /* Вказівник на масив struct media_v2_pad */
    __u32 num_links;        /* Кількість зв'язків (links) */
    __u32 reserved4;
    __u64 ptr_links;        /* Вказівник на масив struct media_v2_link */
};

struct media_v2_entity {
    __u32 id;               /* Унікальний ID entity в системі */
    char name[64];          /* Назва entity (наприклад, "imx219 1-0010") */
    __u32 function;         /* Функціональний тип (MEDIA_ENT_F_CAM_SENSOR, MEDIA_ENT_F_PROC_VIDEO_ISP) */
    __u32 flags;            /* Прапорці стану сутності */
    __u32 reserved[5];
};

struct media_v2_pad {
    __u32 id;               /* Унікальний ID pad у ядрі */
    __u32 entity_id;        /* ID entity, якій належить майданчик */
    __u32 flags;            /* MEDIA_PAD_FL_SINK або MEDIA_PAD_FL_SOURCE */
    __u32 index;            /* Локальний порядковий індекс pad на entity (0, 1, 2...) */
    __u32 reserved[4];
};

struct media_v2_link {
    __u32 id;               /* Унікальний ID зв'язку */
    __u32 source_id;        /* ID джерела (Source Pad ID) */
    __u32 sink_id;          /* ID приймача (Sink Pad ID) */
    __u32 flags;            /* MEDIA_LNK_FL_ENABLED, IMMUTABLE, DYNAMIC */
    __u32 reserved[6];
};
