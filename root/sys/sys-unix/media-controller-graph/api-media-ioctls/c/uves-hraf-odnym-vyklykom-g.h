struct media_v2_entity {
        __u32 id; char name[64]; __u32 function; __u32 flags; __u32 reserved[5];
} __attribute__ ((packed));

struct media_v2_interface {
        __u32 id; __u32 intf_type; __u32 flags; __u32 reserved[9];
        union {
                struct { __u32 major, minor; } devnode;   /* вузол у /dev */
                __u32 raw[16];
        };
} __attribute__ ((packed));

struct media_v2_pad {
        __u32 id; __u32 entity_id; __u32 flags; __u32 index; __u32 reserved[4];
} __attribute__ ((packed));

struct media_v2_link {
        __u32 id; __u32 source_id; __u32 sink_id; __u32 flags; __u32 reserved[6];
} __attribute__ ((packed));

struct media_v2_topology {
        __u64 topology_version;
        __u32 num_entities;   __u32 reserved1;  __u64 ptr_entities;
        __u32 num_interfaces; __u32 reserved2;  __u64 ptr_interfaces;
        __u32 num_pads;       __u32 reserved3;  __u64 ptr_pads;
        __u32 num_links;      __u32 reserved4;  __u64 ptr_links;
} __attribute__ ((packed));
