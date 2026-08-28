import venv

venv.create(
    env_dir,
    system_site_packages=False,
    clear=False,
    symlinks=False,
    with_pip=False,
    prompt=None,
    upgrade_deps=False,
    scm_ignore_files=frozenset(),
)
