typedef struct __mavlink_field_info {
    const char            *name;
    const char            *print_format;
    mavlink_message_type_t type;
    unsigned int           array_length;
    unsigned int           wire_offset;
    unsigned int           structure_offset;
} mavlink_field_info_t;

typedef struct __mavlink_message_info {
    uint32_t             msgid;
    const char          *name;
    unsigned             num_fields;
    mavlink_field_info_t fields[MAVLINK_MAX_FIELDS];
} mavlink_message_info_t;
