count=0

# НЕБЕЗПЕЧНО: конвеєр у POSIX sh породжує подоболонку
cat /etc/passwd | while IFS=: read -r user pass uid gid rest; do
    if [ "$uid" -ge 1000 ]; then
        count=$((count + 1))
    fi
done

echo "Знайдено користувачів: $count"
