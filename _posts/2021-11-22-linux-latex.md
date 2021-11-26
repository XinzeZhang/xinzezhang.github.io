---
title:      Config tex live on Ubuntu
tags:
    -linux
    -tex
---

### TexLive 2021 on ubuntu 20.04 LTS

#### Install iso

To install TeX Live from the ISO file:

```bash
sudo mkdir /media/iso
sudo mount -o loop texlive2021.iso /media/iso/
cd /media/iso
sudo ./install-tl
```

Follow the guidance on the terminal, you will see:

```bash
...
Installing [0060/3252, time/total: 00:10/10:09]: aichej [7k]
Installing [0061/3252, time/total: 00:10/10:09]: ajl [7k]
Installing [0062/3252, time/total: 00:10/10:09]: akktex [16k]
Installing [0063/3252, time/total: 00:10/10:09]: akletter [208k]
Installing [0064/3252, time/total: 00:10/10:05]: alegreya [4672k]
Installing [0065/3252, time/total: 00:11/09:47]: aleph [31k]
...
```

After the installation, unmount the iso with:

```bash
sudo umount /media/iso
```

### Config the env path

Add the following paths in your bash (or zsh) profile file:

```bash
PATH="/usr/local/texlive/2021/bin/x86_64-linux:$PATH"; export PATH
MANPATH="/usr/local/texlive/2021/texmf-dist/doc/man:$MANPATH"; export MANPATH
INFOPATH="/usr/local/texlive/2021/texmf-dist/doc/info:$INFOPATH"; export INFOPATH%
```

### Config the font cache for xelatex and lualatex

If you want to use the system font for xelatex and luatex for all users, copy the tex font config file to the system configs:

```bash
sudo cp /usr/local/texlive/2021/textmf-var/fonts/conf/texlive-fontconfig.conf /etc/fonts/conf.d/09-texlive.conf
sudo fc-cache -fsv
```

Or, if your want to use the font for yourself, just add the font config to the home:

```bash
sudo cp /usr/local/texlive/2021/textmf-var/fonts/conf/texlive-fontconfig.conf ~/.fonts.conf
fc-cache -fv
```

### Config formatting in the VS Code

Install the following modules:

```bash
sudo cpan YAML::Tiny
sudo cpan File::HomeDir
sudo cpan Unicode::GCString
```

### Update tlmgr

Update the packages from the CTAN mirros (you can choose the faster mirrors in  https://ctan.org/mirrors), in this case, I choose the aliyun:

```bash
tlmgr option repository https://mirrors.aliyun.com/CTAN/systems/texlive/tlnet/
```
