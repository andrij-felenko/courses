# Термінал 1: Запуск першого вузла (створення мережі як Leader)
$ ./ot-cli-ftd 1
> dataset init new
> dataset commit active
> ifconfig up
> thread start
> state
leader
> ipaddr mleid
fdde:ad00:beef:0:166e:a00:0:1

# Термінал 2: Запуск другого вузла (підключення як Child/Router)
$ ./ot-cli-ftd 2
> dataset set active <шістнадцятковий_дамп_з_вузла_1>
> ifconfig up
> thread start
> state
child
> udp open
> udp bind :: 12345
> udp send fdde:ad00:beef:0:166e:a00:0:1 12345 "Привіт від вузла 2!"
