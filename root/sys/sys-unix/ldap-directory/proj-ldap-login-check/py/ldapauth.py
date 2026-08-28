# ldapauth.py — той самий алгоритм на ldap3.  pip install ldap3
import ssl
from enum import Enum

from ldap3 import SIMPLE, SUBTREE, Connection, Server, Tls
from ldap3.core.exceptions import (LDAPException, LDAPInvalidCredentialsResult,
                                   LDAPSizeLimitExceededResult)
from ldap3.utils.conv import escape_filter_chars

HOST    = 'ldap.corp.example'
CA_FILE = '/etc/ssl/certs/corp-ca.pem'
BASE_DN = 'ou=people,dc=corp,dc=example'
SVC_DN  = 'cn=login-check,ou=services,dc=corp,dc=example'


class Auth(Enum):
    OK = 'ok'
    DENIED = 'denied'
    NO_ENTRY = 'no-entry'
    AMBIGUOUS = 'ambiguous'
    UNAVAILABLE = 'unavailable'


def _server() -> Server:
    # validate за замовчуванням — ssl.CERT_NONE: сертифікат ніхто не звірятиме,
    # доки цього не написати руками. valid_names — окрема вимога: підпис
    # правильний ще не означає, що це той сервер.
    tls = Tls(validate=ssl.CERT_REQUIRED, ca_certs_file=CA_FILE,
              valid_names=[HOST])
    return Server(HOST, port=389, use_ssl=False, tls=tls, connect_timeout=5)


def _connect(dn: str, password: str) -> Connection:
    conn = Connection(_server(), user=dn, password=password,
                      authentication=SIMPLE, raise_exceptions=True,
                      receive_timeout=5)
    conn.open()        # TCP; тут же спрацює connect_timeout
    conn.start_tls()   # шифрування до того, як на дріт потрапить пароль
    conn.bind()        # і аж тепер пароль
    return conn        # кроки розписані навмисно: auto_bind згортає будь-який
                       # збій в одну помилку, а нам потрібен саме код 49


def check_login(login: str, password: str, svc_password: str) -> Auth:
    # RFC 4513 §5.1.2: порожній пароль — не хибний секрет, а неавтентифіковане
    # прив'язування. Відкидаємо ДО мережі й для обох паролів — але порожній
    # службовий пароль це наша несправність, а не відмова людині.
    if not svc_password:
        return Auth.UNAVAILABLE
    if not login or not password:
        return Auth.DENIED

    query = '(&(objectClass=posixAccount)(uid=%s))' % escape_filter_chars(login)
    try:
        with _connect(SVC_DN, svc_password) as svc:
            svc.search(BASE_DN, query, search_scope=SUBTREE, size_limit=2)
            found = [r for r in (svc.response or [])
                     if r.get('type') == 'searchResEntry']
            if not found:
                return Auth.NO_ENTRY
            if len(found) > 1:
                return Auth.AMBIGUOUS
            user_dn = found[0]['dn']
    except LDAPSizeLimitExceededResult:
        return Auth.AMBIGUOUS
    except LDAPException:            # і недосяжність, і збій TLS, і брак прав
        return Auth.UNAVAILABLE

    try:
        with _connect(user_dn, password):
            return Auth.OK
    except LDAPInvalidCredentialsResult:
        return Auth.DENIED
    except LDAPException:
        return Auth.UNAVAILABLE
