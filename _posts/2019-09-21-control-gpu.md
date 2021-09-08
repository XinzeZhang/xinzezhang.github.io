---

title:   Controlling NVIDIA GPU Fans and Clock remotely
tags:
    -nvidia
    -linux
---

## Acknowledgment
This article is based on the post [*Controlling NVIDIA GPU Fans on a headless Ubuntu system*](http://bailiwick.io/2019/09/21/controlling-nvidia-gpu-fans-on-a-headless-ubuntu-system/) by James Conner.

### Usage

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

Third: create the script to control the gpu clock and the fan speed. And the context can be as follows:

```bash
sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings -a '[gpu:0]/GPUFanControlState=1' -a '[fan:0]/GPUTargetFanSpeed=85'
sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings -a '[gpu:1]/GPUFanControlState=1' -a '[fan:1]/GPUTargetFanSpeed=85'


sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffset[4]=-400' -a '[gpu:0]/GPUMemoryTransferRateOffset[4]=3200'
sudo DISPLAY=:0 XAUTHORITY=/run/user/110/gdm/Xauthority nvidia-settings -a '[gpu:1]/GPUGraphicsClockOffset[4]=-400' -a '[gpu:1]/GPUMemoryTransferRateOffset[4]=3200'
```

Fourth: execute the script.
