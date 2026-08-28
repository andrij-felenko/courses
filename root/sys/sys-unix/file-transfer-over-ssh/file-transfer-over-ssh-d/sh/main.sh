# 1. Створення користувача без права входу в командну оболонку
useradd -m -g sftponly -s /usr/sbin/nologin sftpuser

# 2. Налаштування кореня chroot (тільки root!)
chown root:root /var/sftp/sftpuser
chmod 0755 /var/sftp/sftpuser

# 3. Створення каталогу для файлів із правами користувача
mkdir -p /var/sftp/sftpuser/uploads
chown sftpuser:sftponly /var/sftp/sftpuser/uploads
chmod 0775 /var/sftp/sftpuser/uploads
