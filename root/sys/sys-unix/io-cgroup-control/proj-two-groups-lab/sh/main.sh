delta() {                                  # delta <група> [секунд]
  local f="$CG/$1/io.stat" sec=${2:-5} a b
  read -r _ a < <(grep "^$MAJMIN " "$f"); sleep "$sec"
  read -r _ b < <(grep "^$MAJMIN " "$f")
  awk -v s="$sec" -v A="$a" -v B="$b" 'BEGIN{
      n=split(A,x," "); split(B,y," ")
      for(i=1;i<=n;i++){ split(x[i],p,"="); split(y[i],q,"=")
        printf "%s=%.0f/с ", p[1], (q[2]-p[2])/s }
      print "" }'
}
