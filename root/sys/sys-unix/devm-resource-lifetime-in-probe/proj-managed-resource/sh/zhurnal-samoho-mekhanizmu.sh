$ grep DEBUG_DEVRES /boot/config-$(uname -r)
CONFIG_DEBUG_DEVRES=y
$ sudo rmmod stend && sudo insmod stend.ko      # знову без zlamaty
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/unbind
$ echo 1 | sudo tee /sys/module/devres/parameters/log
$ echo devres-stend | sudo tee /sys/bus/platform/drivers/devres-stend/bind
$ dmesg | grep DEVRES
devres-stend devres-stend: DEVRES ADD ffff888107a4e300 devm_kzalloc_release (112 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e380 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e400 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e480 kanal_release (4 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e500 devm_kzalloc_release (256 bytes)
devres-stend devres-stend: DEVRES ADD ffff888107a4e580 stend_zupynyty (16 bytes)
devres-stend devres-stend: DEVRES REM ffff888107a4e400 kanal_release (4 bytes)
