# разово, до перезавантаження
sudo sysctl -w kernel.randomize_va_space=2

# назавжди
echo 'kernel.randomize_va_space = 2' | sudo tee /etc/sysctl.d/60-aslr.conf
sudo sysctl --system

# перевірити чинне (mmap_rnd_bits читається лише з-під root)
cat /proc/sys/kernel/randomize_va_space
sudo cat /proc/sys/vm/mmap_rnd_bits
