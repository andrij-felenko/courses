$ systemd-analyze critical-chain
graphical.target @9.204s
└─multi-user.target @9.203s
  └─snapd.service @8.317s +884ms
    └─basic.target @8.301s
      └─sockets.target @8.299s
        └─snapd.socket @8.291s +7ms
          └─sysinit.target @8.276s
            └─systemd-timesyncd.service @7.802s +472ms
              └─local-fs.target @7.749s
