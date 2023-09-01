---
title:   Controlling NVIDIA GPU Fans and Clock remotely
tags:
    -nvidia
    -linux
---
## Acknowledgment

This article is based on the post [*Controlling NVIDIA GPU Fans on a headless Ubuntu system*](http://bailiwick.io/2019/09/21/controlling-nvidia-gpu-fans-on-a-headless-ubuntu-system/) by James Conner.

### nvidia-xconfig

#### First: enable the cool-bits

```bash
$ sudo nvidia-xconfig -a --cool-bits=28
```

#### Second: edit the xorg file

```bash
$ sudo nano /etc/X11/xorg.conf
```

Scroll down till you find Section "Screen"

```bash
Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    Monitor        "Monitor0"
    DefaultDepth    24
    Option         "Coolbits" "28"
    SubSection     "Display"
        Depth       24
    EndSubSection
EndSection
```

<!-- Add the following under the line of `Option "Coolbits" "28"` (not necessary)

```bash
Option         "RegistryDwords" "PowerMizerEnable=0x1; PerfLevelSrc=0x2222; PowerMizerDefaultAC=0x1"
``` -->
Check the `/etc/X11/Xwrapper.config` file, if not existing, then create it by `sudo nano /etc/X11/Xwrapper.config`. 
Make sure the following contents in the `Xwrapper.config`, if not, add them.

```bash
needs_root_rights=yes
allowed_users=console
```


#### Third: reboot

### nvidia-settings

To control the fan speed or overclock the nvidia gpu on ubuntu 20.04 remotely via ssh, we need utilizes the nvidia-settings command with the xauth credentials of the Gnome Desktop Manager account.

First: get the user id for the gdm desktop

```bash
$ id gdm

uid=110(gdm) gid=116(gdm) groups=116(gdm)
```

Second: verify the gdm user has an Authority file

```bash
$ sudo ls -AFlh /run/user/110/gdm/

total 4.0K
-rwx------ 1 gdm gdm 108 Sep  7 20:48 Xauthority*
```

Third: create the script `oc.sh` to control the gpu clock and the fan speed. And the context can be as follows:

```bash
for i in "$@"; do
    sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings \
    -a "[gpu:$i]/GPUGraphicsClockOffset[4]=-400" \
    -a "[gpu:$i]/GPUMemoryTransferRateOffset[4]=3200" \
    -a "[gpu:$i]/GPUFanControlState=1" \
    -a "[fan:$i]/GPUTargetFanSpeed=85" 
done
```

Fourth: execute the script.

```bash
$ sh oc.sh 0 1 2
```

BTW: to revert the fan setting, execute the  command in the following manner

```bash
$ sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings -a '[gpu:0]/GPUFanControlState=0'
```

Sometimes, you need to restart gdm service to execute the above mentioned commands.

```bash
sudo systemctl restart gdm
```
