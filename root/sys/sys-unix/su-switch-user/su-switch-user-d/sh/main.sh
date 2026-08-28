$ id -un; pwd; echo $PATH
andrij
/home/andrij/work
/home/andrij/bin:/usr/local/bin:/usr/bin:/bin

$ su -c 'id -un; pwd; echo $PATH' postgres
postgres
/home/andrij/work
/home/andrij/bin:/usr/local/bin:/usr/bin:/bin

$ su - postgres -c 'id -un; pwd; echo $PATH'
postgres
/var/lib/postgresql
/usr/local/bin:/usr/bin:/bin
