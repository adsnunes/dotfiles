#!/bin/sh
# Liga os arquivos deste repositório em ~/.config e ~/.local/bin. O que já existir vai para ~/.config-backup/<data>/.
set -eu
dots=$(cd "$(dirname "$0")" && pwd)
bak="$HOME/.config-backup/$(date +%Y%m%d-%H%M%S)"

link() {
  src="$dots/$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  if [ -e "$dst" ] && [ "$(readlink -f "$dst")" != "$src" ]; then
    mkdir -p "$bak"
    mv "$dst" "$bak/"
  fi
  ln -sfn "$src" "$dst"
}

link i3/config "$HOME/.config/i3/config"
link alacritty/alacritty.toml "$HOME/.config/alacritty/alacritty.toml"
link polybar/config.ini "$HOME/.config/polybar/config.ini"
link rofi/config.rasi "$HOME/.config/rofi/config.rasi"
link dunst/dunstrc "$HOME/.config/dunst/dunstrc"
link picom/picom.conf "$HOME/.config/picom/picom.conf"
link fastfetch/config.jsonc "$HOME/.config/fastfetch/config.jsonc"
link nvim/init.lua "$HOME/.config/nvim/init.lua"
link btop/themes "$HOME/.config/btop/themes"
link yazi/theme.toml "$HOME/.config/yazi/theme.toml"
link newsboat/config "$HOME/.config/newsboat/config"
link newsboat/urls "$HOME/.config/newsboat/urls"
link mpv/mpv.conf "$HOME/.config/mpv/mpv.conf"
for f in theme menu media shot lock wall agents focus notify np; do link "bin/$f" "$HOME/.local/bin/$f"; done

mkdir -p "$HOME/.config/dunst/dunstrc.d" "$HOME/.config/cava"
[ -f "$HOME/.config/btop/btop.conf" ] || cp "$dots/btop/btop.conf" "$HOME/.config/btop/btop.conf"
[ -f "$HOME/.config/i3/local.conf" ] || cp "$dots/i3/local.conf.example" "$HOME/.config/i3/local.conf"
grep -q 'dotfiles/bash/prompt.sh' "$HOME/.bashrc" 2>/dev/null ||
  printf '\n[ -f %s/bash/prompt.sh ] && . %s/bash/prompt.sh\n' "$dots" "$dots" >>"$HOME/.bashrc"

"$dots/bin/theme" dark
echo "ok. backup (se houve): $bak"
