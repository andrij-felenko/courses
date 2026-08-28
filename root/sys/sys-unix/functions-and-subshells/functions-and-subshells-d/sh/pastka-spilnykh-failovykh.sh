# Батько відкриває файл на читання
exec 3< /tmp/data.txt

# Підоболонка читає перший рядок через дескриптор 3
(
    read -r line_child <&3
    echo "Child read: $line_child"
)

# Батько читає наступний рядок
read -r line_parent <&3
echo "Parent read: $line_parent"

exec 3<&-
