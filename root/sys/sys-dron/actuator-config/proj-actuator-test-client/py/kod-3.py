def function_name(f):
    """Людські підписи борт віддає окремим описом; клієнтові досить номерів."""
    if 101 <= f <= 112:
        return 'Motor %d' % (f - 100)
    if 201 <= f <= 215:
        return 'Servo %d' % (f - 200)
    return 'функція %d' % f if f else 'вимкнено'


def main(argv):
    link = mavutil.mavlink_connection(argv[1] if len(argv) > 1 else 'udpin:0.0.0.0:14550',
                                      source_system=255)
    link.wait_heartbeat()
    print('борт %d' % link.target_system)

    outputs = read_output_functions(link)
    if len(argv) < 3:
        order = lambda n: (0 if 'MAIN' in n else 1, int(n.split('FUNC')[1]))
        for name in sorted(outputs, key=order):
            f = outputs[name]
            if f:                             # нуль означає «вихід не задіяно»
                print('  %-16s = %-5d %s' % (name, f, function_name(f)))
        return 0

    function = int(argv[2])
    value = float(argv[3]) if len(argv) > 3 else 0.15
    seconds = float(argv[4]) if len(argv) > 4 else 3.0
    if function not in outputs.values():
        print('увага: функцію %d не призначено жодному виходу' % function, file=sys.stderr)

    print('крутимо %s на %.2f протягом %.1f с' % (function_name(function), value, seconds))
    return run_test(link, function, value, seconds)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
