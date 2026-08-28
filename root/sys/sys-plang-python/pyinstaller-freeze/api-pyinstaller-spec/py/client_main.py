# Багатоцільова збірка клієнта та демона в єдиному каталозі dist/my_suite/
a_client = Analysis(['src/client_main.py'], pathex=['src'], datas=[('assets/*', 'assets')])
pyz_client = PYZ(a_client.pure, a_client.zipped_data)
exe_client = EXE(pyz_client, a_client.scripts, exclude_binaries=True, name='client', console=False)

a_server = Analysis(['src/server_daemon.py'], pathex=['src'])
pyz_server = PYZ(a_server.pure, a_server.zipped_data)
exe_server = EXE(pyz_server, a_server.scripts, exclude_binaries=True, name='server', console=True)

coll = COLLECT(
    exe_client, a_client.binaries, a_client.zipfiles, a_client.datas,
    exe_server, a_server.binaries, a_server.zipfiles, a_server.datas,
    strip=False, upx=True, name='my_suite'
)
