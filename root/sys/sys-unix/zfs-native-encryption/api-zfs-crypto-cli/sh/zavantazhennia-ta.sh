# zfs get -r encryption,keystatus,keylocation,encryptionroot pool
NAME                      PROPERTY        VALUE                           SOURCE
pool                      encryption      off                             default
pool/securedataset        encryption      on                              local
pool/securedataset        keystatus       available                       -
pool/securedataset        keylocation     prompt                          local
pool/securedataset        encryptionroot  pool/securedataset              -
pool/securedataset/home   encryption      on                              inherited from pool/securedataset
pool/securedataset/home   keystatus       available                       -
pool/securedataset/home   keylocation     prompt                          local
pool/securedataset/home   encryptionroot  pool/securedataset              -
