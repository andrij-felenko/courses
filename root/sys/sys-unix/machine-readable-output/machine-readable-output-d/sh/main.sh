$ lsblk -J -b -o NAME,SIZE,MOUNTPOINT
{
   "blockdevices": [
      {
         "name": "sda",
         "size": 2000398934016,
         "mountpoint": null,
         "children": [
            {
               "name": "sda1",
               "size": 536870912,
               "mountpoint": "/boot/efi"
            },
            {
               "name": "sda2",
               "size": 1999860498432,
               "mountpoint": "/"
            }
         ]
      }
   ]
}
