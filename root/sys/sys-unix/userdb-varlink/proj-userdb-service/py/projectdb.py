#!/usr/bin/env python3
"""projectdb.py — та сама служба, коротше: реєстр проєктів як користувачі.
   запустити: sudo python3 projectdb.py
   спитати:   userdbctl user proj-kernel
"""
import json, os, socket, struct

SERVICE    = "com.example.Projects"
SOCKPATH   = "/run/systemd/userdb/" + SERVICE
UID_BASE   = 55000                 # діапазон, не виданий на цій машині нікому
PROJECTS   = ["kernel", "toolchain", "docs"]
DEPLOY_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIexample ci@build"


def resolve(p, name_key, num_key):
    """Індекс проєкту, None (такого немає) або "all" (просять перелік)."""
    if name_key in p:
        n = p[name_key]
        tail = n[5:] if n.startswith("proj-") else None
        return PROJECTS.index(tail) if tail in PROJECTS else None
    if num_key in p:
        i = p[num_key] - UID_BASE
        return i if 0 <= i < len(PROJECTS) else None
    return "all"


def user_record(i, peer):
    uid = UID_BASE + i
    rec = {
        "userName": f"proj-{PROJECTS[i]}",
        "realName": f"Проєкт {PROJECTS[i]}",
        "disposition": "system",
        "service": SERVICE,
        "uid": uid, "gid": uid,
        "homeDirectory": f"/var/lib/projects/{PROJECTS[i]}",
        "shell": "/usr/sbin/nologin",
    }
    owner = peer in (0, uid)              # власник запису або root
    if owner:
        rec["privileged"] = {"sshAuthorizedKeys": [DEPLOY_KEY]}
    return {"record": rec, "incomplete": not owner}


def group_record(i):
    return {"record": {"groupName": f"proj-{PROJECTS[i]}", "disposition": "system",
                       "service": SERVICE, "gid": UID_BASE + i},
            "incomplete": False}


def send(conn, obj):
    conn.sendall(json.dumps(obj).encode() + b"\0")     # роздільник — нульовий байт


def error(conn, name):
    send(conn, {"error": name, "parameters": {}})


def stream(conn, make, n):
    for k in range(n):
        reply = {"parameters": make(k)}
        if k + 1 < n:
            reply["continues"] = True                  # ще не остання
        send(conn, reply)


def serve(conn):
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    _pid, peer, _gid = struct.unpack("3i", raw)        # засвідчено ядром

    buf = b""
    while b"\0" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return
        buf += chunk
    call = json.loads(buf.split(b"\0", 1)[0])
    p = call.get("parameters") or {}

    if p.get("service") != SERVICE:
        return error(conn, "io.systemd.UserDatabase.BadService")

    method = call.get("method")

    if method == "io.systemd.UserDatabase.GetUserRecord":
        i = resolve(p, "userName", "uid")
        if i == "all":
            if not call.get("more"):
                return error(conn, "org.varlink.service.InvalidParameter")
            return stream(conn, lambda k: user_record(k, peer), len(PROJECTS))
        if i is None:
            return error(conn, "io.systemd.UserDatabase.NoRecordFound")
        return send(conn, {"parameters": user_record(i, peer)})

    if method == "io.systemd.UserDatabase.GetGroupRecord":
        i = resolve(p, "groupName", "gid")
        if i == "all":
            if not call.get("more"):
                return error(conn, "org.varlink.service.InvalidParameter")
            return stream(conn, group_record, len(PROJECTS))
        if i is None:
            return error(conn, "io.systemd.UserDatabase.NoRecordFound")
        return send(conn, {"parameters": group_record(i)})

    if method == "io.systemd.UserDatabase.GetMemberships":
        return error(conn, "io.systemd.UserDatabase.NoRecordFound")

    error(conn, "org.varlink.service.MethodNotFound")


if __name__ == "__main__":
    if os.path.exists(SOCKPATH):
        os.unlink(SOCKPATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCKPATH)
    os.chmod(SOCKPATH, 0o666)          # хто питає — будь-хто; що почує — за peer
    srv.listen(64)
    while True:
        conn, _ = srv.accept()
        with conn:
            try:
                serve(conn)
            except Exception:          # зіпсований запит не валить служби
                pass
