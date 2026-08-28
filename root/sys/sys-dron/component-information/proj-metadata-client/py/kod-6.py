def describe(p):
    out = ['%s  (%s)' % (p['name'], p.get('type', '?')),
           '  підпис   : %s' % p.get('shortDesc', '—')]
    if p.get('units'):
        out.append('  одиниці  : %s' % p['units'])
    if 'min' in p or 'max' in p:
        out.append('  межі     : %s … %s' % (p.get('min', '−∞'), p.get('max', '+∞')))
    if 'default' in p:
        out.append('  усталене : %s' % p['default'])
    if p.get('group'):
        out.append('  група    : %s' % p['group'])
    if p.get('rebootRequired'):
        out.append('  ! потрібне перезавантаження')
    for v in p.get('values', []):
        out.append('    %s = %s' % (v['value'], v['description']))
    return '\n'.join(out)


def main(device, wanted):
    link = mavutil.mavlink_connection(device, source_system=255)
    link.wait_heartbeat()                            # звідси відомий target_system

    meta = request_message(link, 397, 'COMPONENT_METADATA')
    if meta is None:
        sys.exit('апарат не віддав COMPONENT_METADATA')

    # 0 — COMP_METADATA_TYPE_GENERAL; запасної адреси в покажчика немає за задумом
    general_raw = fetch_cached(link, 0, [(cstr(meta.uri), meta.file_crc)])
    if general_raw is None:
        sys.exit('не вдалося взяти файл-покажчик')
    general = json.loads(general_raw)

    sources = sources_for(general, 1)                # 1 — COMP_METADATA_TYPE_PARAMETER
    if sources is None:
        sys.exit('апарат не описує своїх параметрів')

    params_raw = fetch_cached(link, 1, sources)
    if params_raw is None:
        sys.exit('не вдалося взяти описи параметрів')

    for p in json.loads(params_raw).get('parameters', []):
        if p.get('name') == wanted:
            print(describe(p))
            return
    print('немає такого параметра:', wanted)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'udpin:0.0.0.0:14550',
         sys.argv[2] if len(sys.argv) > 2 else 'MPC_XY_P')
