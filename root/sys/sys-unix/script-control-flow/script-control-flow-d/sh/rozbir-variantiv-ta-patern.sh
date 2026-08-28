file_type="archive.tar.gz"

case "$file_type" in
    *.tar.gz|*.tgz)
        tar -xzf "$file_type"
        ;;
    *.zip)
        unzip -q "$file_type"
        ;;
    *.deb|*.rpm)
        echo "Пакет встановлення ПЗ"
        ;;
    *)
        echo "Невідомий формат файлу" >&2
        exit 1
        ;;
esac
