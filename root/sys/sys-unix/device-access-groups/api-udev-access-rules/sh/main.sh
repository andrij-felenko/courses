$ setfacl -m u:andrij:rw,m::r /dev/ttyUSB0
$ getfacl -p /dev/ttyUSB0
# file: /dev/ttyUSB0
# owner: root
# group: dialout
user::rw-
user:andrij:rw-			#effective:r--
group::rw-			#effective:r--
mask::r--
other::---
