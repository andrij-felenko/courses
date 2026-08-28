import multiprocessing as mp

def kill_at_brink(target, args) -> int:
    """Народити писаря, дочекатись його сигналу «я на межі» — і вбити посеред запису.
    target отримує mp.Event 'brink' і має викликати brink.set() РІВНО в небезпечну мить."""
    brink = mp.Event()
    p = mp.Process(target=target, args=(*args, brink))
    p.start()
    assert brink.wait(timeout=5), "писар не дійшов до межі"
    p.kill()                        # SIGKILL / TerminateProcess: не спіймати, не прибрати за собою
    p.join()
    assert p.exitcode not in (0, None)   # дитина померла НЕ штатно — саме цього ми й хотіли
    return p.exitcode
