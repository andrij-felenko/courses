DEV=/dev/nvme0n1                        # ⚠️ цілий пристрій; наступний рядок стирає вміст
MAJMIN=$(lsblk -ndo MAJ:MIN "$DEV")     # 259:0
MNT=/mnt/wblab
mkfs.ext4 -qF "$DEV"; mkdir -p "$MNT"; mount "$DEV" "$MNT"

ROOT=/sys/fs/cgroup; CG=$ROOT/wblab
echo "+memory +io" > "$ROOT/cgroup.subtree_control"
mkdir -p "$CG"/{a,b}
echo "+memory +io" > "$CG/cgroup.subtree_control"

in_cg() { ( echo $BASHPID > "$CG/$1/cgroup.procs"; shift; exec "$@" ); }
