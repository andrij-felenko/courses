# Приклад запуску аудитора у кроці do_rootfs_postprocess
IMAGE_POSTPROCESS_COMMAND += "audit_firmware_licenses; "

audit_firmware_licenses() {
    local rootfs_dir="${IMAGE_ROOTFS}"
    echo "Запуск аудиту бінарників у ${rootfs_dir}/usr/bin..."
    
    find "${rootfs_dir}/usr/bin" -type f -executable | while read -r bin_file; do
        /usr/local/bin/firmware-auditor "${bin_file}" || {
            echo "ПОМИЛКА: Ліцензійне порушення у файлі ${bin_file}!" >&2
            exit 1
        }
    done
}
