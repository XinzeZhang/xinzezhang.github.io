---
title:      Config zsh and tmux on new device
tags:
    -linux
    -zsh
    -tmux
    -cuda
---
### new sudo account

Use the `adduser` command to add a new user to your system.

```
sudo adduser username
```

Set and confirm the new user’s password at the prompt. And use the `usermod` command to add the user to the sudo group.

```
sudo usermod -aG sudo username
```

### zsh

install zsh, autojump and git on server

```
git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting
sudo apt install zsh autojump git
```

scp install to the server from local

```
scp ~/.oh-my-zsh/tools/install.sh pop:~/
```

setup zsh on server

```
sh install.sh
```

transfer plugins to the server

```
scp -P 22 -r ~/.oh-my-zsh/custom/* pop:~/.oh-my-zsh/custom/
```

config zsh theme plugin on the server

```
rm $ZSH_CUSTOM/themes/spaceship.zsh-theme
ln -s "$ZSH_CUSTOM/themes/spaceship-prompt/spaceship.zsh-theme" "$ZSH_CUSTOM/themes/spaceship.zsh-theme"
```

copy the linux zsh configuration to the server

```
scp -P 22 -r ~/.zshrc pop:~/
```

### tmux

scp the plugins to the server from the server machine

```
scp -r ~/.tmux/ pop:~/
```

create the tmux config file

```
touch .tmux.conf
```

copy and paste

```
# Mouse mode
set -g mouse on

set -g base-index 1 # 设置窗口的起始下标为1
set -g pane-base-index 1 # 设置面板的起始下标为1

bind-key k confirm-before kill-window

# Easy config reload
bind-key r source-file ~/.tmux.conf \; display-message "tmux.conf reloaded"

# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
#set -g @plugin 'jimeh/tmux-themepack'
#set -g @themepack 'powerline/double/blue'
source-file ${HOME}/.tmux/plugins/tmux-themepack/powerline/double/blue.tmuxtheme

run -b '~/.tmux/plugins/tpm/tpm'

#-------------------------------------------------------#
#PANE NAVIGATION/MANAGEMENT
#-------------------------------------------------------#
# splitting panes
bind h split-window -h   # Split panes horizontal
bind v split-window -v   # Split panes vertically

# open new panes in current path
bind c new-window -c '#{pane_current_path}'

# Use Alt-arrow keys WITHOUT PREFIX KEY to switch panes
bind -n M-4 select-pane -L
bind -n M-6 select-pane -R
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D
#-------------------------------------------------------#
```

### cuda

#### cuda 10.1

```
sudo apt-get install gcc-7 g++-7
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 9
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 1
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 9
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 1

sudo sh cuda_10.1.105_418.39_linux.run

tar zxvf ./cudnn-10.1-linux-x64-v7.6.5.32.tgz -C ./

sudo cp cuda/include/cudnn.h /usr/local/cuda/include

sudo cp cuda/lib64/* /usr/local/cuda/lib64/

sudo chmod 755 /usr/local/cuda/include/cudnn.h /usr/local/cuda/lib64/libcudnn*

```
