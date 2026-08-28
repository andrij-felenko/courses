#define NLA_ALIGNTO     4
#define NLA_ALIGN(len)  (((len) + NLA_ALIGNTO - 1) & ~(NLA_ALIGNTO - 1))
#define NLA_HDRLEN      ((int) NLA_ALIGN(sizeof(struct nlattr)))
#define NLA_DATA(nla)   ((void *)((char *)(nla) + NLA_HDRLEN))
#define NLA_PAYLOAD(nla) ((int)((nla)->nla_len - NLA_HDRLEN))
#define NLA_NEXT(nla,len) ((len) -= NLA_ALIGN((nla)->nla_len), \
                          (struct nlattr *)(((char *)(nla) + NLA_ALIGN((nla)->nla_len))))
#define NLA_OK(nla,len) ((len) >= (int)sizeof(struct nlattr) && \
                         (nla)->nla_len >= sizeof(struct nlattr) && \
                         (nla)->nla_len <= (len))
