---
title:      Config KVM and DSM on Ubuntu
tags:
    -linux
    -kvm
---


### KVM on ubuntu 20.04 LTS

#### initial

```bash
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager
```

- `qemu-kvm` - software that provides hardware emulation for the KVM hypervisor.
- `libvirt-daemon-system` - configuration files to run the libvirt daemon as a system service.
- `libvirt-clients` - software for managing virtualization platforms.
- `bridge-utils` - a set of command-line tools for configuring ethernet bridges.
- `virtinst` - a set of command-line tools for creating virtual machines.
- `virt-manager` - an easy-to-use GUI interface and supporting command-line utilities for managing virtual machines through libvirt.

Once the packages are installed, the libvirt daemon will start automatically. You can verify it by typing:

```bash
sudo systemctl is-active libvirtd
```

To be able to create and manage virtual machines, you’ll need to add your user to the “libvirt” and “kvm” groups. To do that, enter:

```
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
```

#### create a network bridge on the host

first install the network bridge utilities package for debugging.

```
sudo apt-get install bridge-utils
```

Next, we need to disable the default networking that KVM installed for itself. You can use `ip a` to see what the default network looks like:

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether d4:be:d9:f3:1e:5f brd ff:ff:ff:ff:ff:ff
6: virbr0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP mode DEFAULT group default qlen 1000
    link/ether 52:54:00:1d:5b:25 brd ff:ff:ff:ff:ff:ff
7: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc fq_codel master virbr0 state DOWN mode DEFAULT group default qlen 1000
    link/ether 52:54:00:1d:5b:25 brd ff:ff:ff:ff:ff:ff
```

The entries `virbr0` and `virbr0-nic` are what KVM installs by default, which are need to be removed.

```
sudo virsh net-destroy default
sudo virsh net-undefine default
```

Now you can run `ip` again and the `virbr0` and `virbr0-nic` should be gone.

Next, we will need to set up a bridge to use when we create a VM.

Edit your `/etc/netplan/01-network-manager-all.yaml` (after making a back-up) to add a bridge. This is what mine looks like after editing:

```
network:
  version: 2
  renderer: NetworkManager

  ethernets:
    enp39s0:
      dhcp4: false
      dhcp6: false

  bridges:
    br0:
      interfaces: [enp39s0]
      addresses: [192.168.0.123/24]
      gateway4: 192.168.0.1
      mtu: 1500
      nameservers:
        addresses: [202.114.0.131,202.114.0.242]
      parameters:
        stp: true
        forward-delay: 4
      dhcp4: no
      dhcp6: no
```

Now run `sudo netplan apply` to apply your new configuration. You can use the `ifconfig` command to inspect that it looks corrent:

```
br0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.11  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::82ea:7ff:fe87:1950  prefixlen 64  scopeid 0x20<link>
        ether 80:ea:07:87:19:50  txqueuelen 1000  (Ethernet)
        RX packets 544019  bytes 786490484 (786.4 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 274804  bytes 20212969 (20.2 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

enp4s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether 80:ea:07:87:19:50  txqueuelen 1000  (Ethernet)
        RX packets 550954  bytes 795441951 (795.4 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 279363  bytes 22237539 (22.2 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 568  bytes 52947 (52.9 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 568  bytes 52947 (52.9 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

vnet0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::fc54:ff:fe67:4e62  prefixlen 64  scopeid 0x20<link>
        ether fe:54:00:67:4e:62  txqueuelen 1000  (Ethernet)
        RX packets 3051  bytes 1810805 (1.8 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2830  bytes 828417 (828.4 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

### Autostart vm guests

Add the command to `/etc/rc.local` with:

```bash
sudo nano /etc/rc.local
```

This file will executes the command as root when boot-up.

Note that, a shebang line that is `#!/bin/bash` should be checked at the top of the `rc.local`, if not exists, add it as the first line of the `rc.local`.

Then, ensure the file is executable:

```bash
sudo chmod a+x /etc/rc.local
```

After that, add the comand `virsh start vmname` to the `rc.local`, where the `vmname` is the name of the vm guest.


#### disk pass through

get the disk id by :

```
ls -l /dev/disk/by-id/
```

then just fill the disk device address in virt-manager, like:

```
/dev/disk/by-id/ata-ST4000VX007-2DT166_ZGY7CTQ9
/dev/disk/by-id/ata-ST4000VX007-2DT166_ZGY7D8FZ
```

when you add the storage and off you go.

### dsm

#### moments cannot figure out and recognize the person and themes

first stop the moments service

```
ssh xinze@dsm
sudo -i
mv /var/packages/SynologyMoments/target/usr/lib/libsynophoto-plugin-detection.so /var/packages/SynologyMoments/target/usr/lib/libsynophoto-plugin-detection.so.bak
scp xinze@192.168.0.10:/Users/xinze/Downloads/libsynophoto-plugin-detection.so /var/packages/SynologyMoments/target/usr/lib/
cd /var/packages/SynologyMoments/target/usr/lib
chgrp SynologyMoments libsynophoto-plugin-detection.so
chown SynologyMoments libsynophoto-plugin-detection.so
chmod 755 libsynophoto-plugin-detection.so
```

using `stat libsynophoto-plugin-detection.so` to check the file property, if ok, restart the moments.
