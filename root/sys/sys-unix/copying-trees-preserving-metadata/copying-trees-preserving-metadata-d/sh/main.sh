tar --create --file=- \
    --directory=/source \
    --acls \
    --xattrs \
    --selinux \
    --sparse \
    . | tar --extract --file=- \
            --directory=/destination \
            --preserve-permissions \
            --same-owner \
            --acls \
            --xattrs \
            --selinux \
            --sparse
