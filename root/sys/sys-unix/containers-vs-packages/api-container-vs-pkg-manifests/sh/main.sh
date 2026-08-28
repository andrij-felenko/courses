# Перегляд метаданих та залежностей пакунка .deb
dpkg-deb -I package.deb control

# Список усіх файлів усередині пакунка .deb
dpkg-deb -c package.deb

# Перегляд заголовків та метаданих пакунка .rpm
rpm -qpi package.rpm

# Перегляд списку файлів усередині пакунка .rpm
rpm -qpl package.rpm
