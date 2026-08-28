$ setfacl -m u:hanna:rw report.csv
$ getfacl report.csv
# file: report.csv
# owner: bohdan
# group: staff
user::rw-
user:hanna:rw-
group::r--
mask::rw-
other::---

$ ls -l report.csv
-rw-rw----+ 1 bohdan staff 8192 report.csv
