struct acpi_buffer out = { ACPI_ALLOCATE_BUFFER, NULL };
acpi_status status = wmidev_block_query(wdev, 0, &out);

if (ACPI_SUCCESS(status) && out.pointer) {
    union acpi_object *obj = out.pointer;
    if (obj->type == ACPI_TYPE_BUFFER) {
        u16 *utf16_str = (u16 *)obj->buffer.pointer;
        char utf8_buf[256];

        /* Конвертація UTF-16LE у UTF-8 для використання в Linux */
        utf16s_to_utf8s(utf16_str, obj->buffer.length / 2,
                        UTF16_LITTLE_ENDIAN, utf8_buf, sizeof(utf8_buf) - 1);
    }
    kfree(out.pointer);
}
