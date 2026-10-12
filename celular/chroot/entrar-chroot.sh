#!/system/bin/sh
# Modo COM ROOT: entra no mesmo Debian do proot-distro, mas por chroot.
# Mais rápido que o proot (sem tradução de chamadas do sistema).
# É chamado pelo tocaia_celular.py via `su -c`:
#   sh entrar-chroot.sh <rootfs> <tmp-do-termux> <usuario>
set -e
R="$1"; TT="$2"; U="${3:-analista}"
[ -d "$R/usr" ] || { echo "Debian não encontrado em $R. Rode: tocaia_celular.py instalar"; exit 1; }

montar() { # montar <origem> <destino> [tipo]
  mkdir -p "$2"
  if grep -q " $2 " /proc/mounts; then return 0; fi
  if [ -n "$3" ]; then mount -t "$3" "$3" "$2"; else mount --bind "$1" "$2"; fi
}

# /data no Android vem montado com nosuid,nodev: sudo e /dev precisam disso
mount -o remount,dev,suid /data 2>/dev/null || true

montar /dev     "$R/dev"
montar devpts   "$R/dev/pts" devpts
montar proc     "$R/proc"    proc
montar sysfs    "$R/sys"     sysfs
montar /sdcard  "$R/sdcard"
# a /tmp do Termux tem o socket da tela :0 do Termux:X11
montar "$TT"    "$R/tmp"

# DNS: o Android não tem /etc/resolv.conf; o chroot precisa de um
[ -s "$R/etc/resolv.conf" ] || printf 'nameserver 1.1.1.1\nnameserver 9.9.9.9\n' > "$R/etc/resolv.conf"

exec chroot "$R" /bin/su - "$U" -c \
  "export DISPLAY=:0; dbus-launch --exit-with-session xfce4-session"
