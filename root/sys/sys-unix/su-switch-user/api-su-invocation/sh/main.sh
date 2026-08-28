# чи справний службовий запис: пароль, домівка, оболонка — усе за один раз
$ su - postgres -c 'id -un; pwd; echo "$0"'
Password:
postgres
/var/lib/postgresql
-bash

# що саме дістанеться службі: вхідне оточення видно цілком
$ su - postgres -c env | sort

# те саме без пароля, з-під root, для скрипта: інший стек PAM, той самий код
# runuser -l postgres -c 'pg_isready'
