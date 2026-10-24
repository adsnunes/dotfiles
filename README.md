# graphite

i3 on a thinkpad x230. gray, quiet, no icons.

![dark](docs/dark.png)
![light](docs/light.png)

## what's here

- **i3** + **picom**: thin borders, rounded corners, soft shadows, small open/close animations
- **polybar**: words in brackets. `[ AGENTS ]` counts AI agents running in [herdr](https://herdr.dev), local or over ssh
- **alacritty**, **rofi**, **dunst**, **btop**, **cava**, **newsboat**, **mpv**, **fastfetch**, **neovim** (`quiet`)
- **wallpaper**: streamlines of a turbulent flow behind a cylinder (von Kármán street), computed by
  [`wallpapers/flow.py`](wallpapers/flow.py). `python3 flow.py dark 42 > flow.svg` for a new one

## keys

| | |
|---|---|
| `alt enter` | terminal |
| `alt d` | launcher |
| `alt /` | command menu (and the list of keys) |
| `alt t` | light / dark |
| `alt n` | next flow |
| `alt z` | focus mode: bar becomes a 25 min countdown, notifications pause |
| `alt shift s` | screenshot |
| `alt l` | lock |

## install

```sh
sudo pacman -S --needed i3-wm picom polybar rofi dunst alacritty feh maim xclip playerctl \
  btop cava newsboat mpv mpv-mpris yt-dlp fastfetch neovim yazi ttf-jetbrains-mono-nerd
git clone https://github.com/adsnunes/dotfiles ~/.dotfiles
~/.dotfiles/install.sh
```

`install.sh` links everything into `~/.config` and `~/.local/bin` and moves what was there to `~/.config-backup/`.
machine-only stuff (monitors, autostart) goes in `~/.config/i3/local.conf`.
for `[ AGENTS ]` over ssh, put the host in `~/.config/herdr-remote`.
