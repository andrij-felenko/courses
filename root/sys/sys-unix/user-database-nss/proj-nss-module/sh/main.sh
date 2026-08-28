cc -O2 -Wall -shared -fPIC -Wl,-soname,libnss_demo.so.2 \
   -o libnss_demo.so.2 nss_demo.c
sudo install -m 0644 libnss_demo.so.2 /usr/lib/x86_64-linux-gnu/
sudo ldconfig

printf 'builder:6001:6001\nrunner:6002:6002\n' | sudo tee /etc/demo-users
sudo sed -i 's/^passwd:.*/passwd:  files demo/' /etc/nsswitch.conf

getent passwd builder      # builder:*:6001:6001::/srv/proj/builder:/usr/sbin/nologin
id -nu 6002                # runner
