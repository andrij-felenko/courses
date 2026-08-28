# Перевірка вмісту DEB
dpkg-deb -c package.deb
dpkg-deb -I package.deb # Перегляд полів control

# Перевірка вмісту RPM
rpm -qpl package.rpm
rpm -qp --scripts package.rpm # Перегляд скриптів %pre/%post

# Перевірка вмісту архіву
tar -ztvf package.tar.gz
