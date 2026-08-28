#!/usr/bin/env python3
"""Мінімальний вивантажувач місії поверх pymavlink."""
import time
from pymavlink import mavutil

mav = mavutil.mavlink                  # простір імен констант і переліків

ACK_S, ITEM_S, MAX_RETRY = 1.5, 0.25, 5

BLAMED = {
    mav.MAV_MISSION_INVALID_PARAM1:   'param1',
    mav.MAV_MISSION_INVALID_PARAM2:   'param2',
    mav.MAV_MISSION_INVALID_PARAM3:   'param3',
    mav.MAV_MISSION_INVALID_PARAM4:   'param4',
    mav.MAV_MISSION_INVALID_PARAM5_X: 'x (широта)',
    mav.MAV_MISSION_INVALID_PARAM6_Y: 'y (довгота)',
    mav.MAV_MISSION_INVALID_PARAM7:   'z (висота)',
}


class UploadFailed(Exception):
    pass


def prepare(items, home=None):
    """Дім нульовим пунктом і зсув цілей DO_JUMP — раз, до першого кадру."""
    if home is not None:
        shifted = []
        for it in items:
            it = dict(it)
            if it['command'] == mav.MAV_CMD_DO_JUMP:
                p = list(it['params'])
                p[0] += 1                  # ціль поїхала разом з усіма
                it['params'] = p
            shifted.append(it)
        items = [home] + shifted

    for i, it in enumerate(items):
        if it['command'] != mav.MAV_CMD_DO_JUMP:
            continue
        tgt = round(it['params'][0])
        if not 0 <= tgt < len(items):
            raise UploadFailed(f'DO_JUMP у пункті {i} цілить у неіснуючий {tgt}')
    return items


def explain(code, items, last_sent):
    """Код завершення + пункт, на якому він спрацював."""
    entry = mav.enums['MAV_MISSION_RESULT'].get(code)
    head = f'{entry.name} — {entry.description}' if entry else f'невідомий код {code}'
    if code in BLAMED:
        head += f'; винне поле {BLAMED[code]}'
    if last_sent is None:
        return (f'борт відмовив: {head}; жодного пункту ще не віддано — '
                f'причина стосується самого лічильника ({len(items)} пунктів)')
    it = items[last_sent]
    cmd = mav.enums['MAV_CMD'].get(it['command'])
    return (f'борт відмовив: {head}; останній відданий пункт {last_sent}: '
            f'команда {cmd.name if cmd else it["command"]}, '
            f'рамка {it["frame"]}, params={it["params"]}, '
            f'x={it["x"]}, y={it["y"]}, z={it["z"]}')


def upload(conn, items, home=None,
           mission_type=mav.MAV_MISSION_TYPE_MISSION, log=print):
    items = prepare(items, home)
    tsys, tcomp = conn.target_system, conn.target_component

    def send_count():
        conn.mav.mission_count_send(tsys, tcomp, len(items), mission_type)

    def send_item(seq):
        it = items[seq]
        p = it['params']
        conn.mav.mission_item_int_send(
            tsys, tcomp, seq, it['frame'], it['command'],
            0, int(it.get('autocontinue', True)),
            p[0], p[1], p[2], p[3], it['x'], it['y'], it['z'], mission_type)

    def cancel():
        conn.mav.mission_ack_send(tsys, tcomp,
                                  mav.MAV_MISSION_OPERATION_CANCELLED,
                                  mission_type)

    pending = set(range(len(items)))       # черга ще не відданих номерів
    last_sent, retry, expect = None, 0, 'request'

    send_count()
    deadline = time.monotonic() + ACK_S

    while True:
        left = deadline - time.monotonic()
        msg = conn.recv_match(
            type=['MISSION_REQUEST', 'MISSION_REQUEST_INT', 'MISSION_ACK'],
            blocking=True, timeout=left) if left > 0 else None

        if msg is None:                                    # тиша
            if expect == 'ack':
                cancel()
                raise UploadFailed(
                    'борт не надіслав завершального підтвердження; що зараз '
                    'на борту — невідомо, перечитай кількість пунктів')
            retry += 1
            if retry > MAX_RETRY:
                cancel()
                raise UploadFailed(f'немає відповіді після {MAX_RETRY} спроб')
            if last_sent is None:
                send_count()                               # не озвався на лічильник
                deadline = time.monotonic() + ACK_S
            else:
                send_item(last_sent)                       # та сама відповідь ще раз
                deadline = time.monotonic() + ITEM_S
            continue

        if msg.get_srcSystem() != tsys:
            continue
        if getattr(msg, 'mission_type', mission_type) != mission_type:
            continue

        if msg.get_type() in ('MISSION_REQUEST', 'MISSION_REQUEST_INT'):
            seq = msg.seq                       # обидва запити — один обробник,
            if seq >= len(items):               # відповідь завжди _INT
                cancel()
                raise UploadFailed(
                    f'борт просить пункт {seq}, а їх усього {len(items)}')
            retry = 0
            send_item(seq)
            last_sent = seq
            pending.discard(seq)
            if pending:
                expect, deadline = 'request', time.monotonic() + ITEM_S
            else:
                expect, deadline = 'ack', time.monotonic() + ACK_S
            continue

        code = msg.type                                    # MISSION_ACK
        if code != mav.MAV_MISSION_ACCEPTED:
            raise UploadFailed(explain(code, items, last_sent))
        if pending:
            raise UploadFailed(
                f'борт підтвердив місію, не забравши {sorted(pending)}')
        log(f'готово: на борту {len(items)} пунктів')
        return


if __name__ == '__main__':
    conn = mavutil.mavlink_connection(
        'udpout:127.0.0.1:14550', source_system=255,
        source_component=mav.MAV_COMP_ID_MISSIONPLANNER)
    conn.wait_heartbeat()

    def wp(lat, lon, alt):
        return {'command': mav.MAV_CMD_NAV_WAYPOINT,
                'frame': mav.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                'params': [0, 0, 0, 0],
                'x': int(lat * 1e7), 'y': int(lon * 1e7), 'z': alt}

    mission = [
        {'command': mav.MAV_CMD_NAV_TAKEOFF,
         'frame': mav.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
         'params': [0, 0, 0, 0], 'x': 0, 'y': 0, 'z': 30},
        wp(50.4501, 30.5234, 60),
        wp(50.4520, 30.5260, 60),
        {'command': mav.MAV_CMD_DO_JUMP, 'frame': mav.MAV_FRAME_MISSION,
         'params': [1, 3, 0, 0], 'x': 0, 'y': 0, 'z': 0},   # ціль — пункт 1
        {'command': mav.MAV_CMD_NAV_LAND,
         'frame': mav.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
         'params': [0, 0, 0, 0], 'x': 0, 'y': 0, 'z': 0},
    ]
    home = {'command': mav.MAV_CMD_NAV_WAYPOINT, 'frame': mav.MAV_FRAME_GLOBAL,
            'params': [0, 0, 0, 0],
            'x': int(50.4500 * 1e7), 'y': int(30.5230 * 1e7), 'z': 148.0}

    upload(conn, mission, home=home)   # home=None — нумерація без домашнього пункту
