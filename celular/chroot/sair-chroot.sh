#!/system/bin/sh
# Desmonta o chroot da TOCAIA (do mais interno para o mais externo).
#   sh sair-chroot.sh <rootfs>
R="$1"
[ -n "$R" ] || { echo "uso: sair-chroot.sh <rootfs>"; exit 1; }
pkill -f "xfce4-session" 2>/dev/null
sleep 1
for m in tmp sdcard sys proc dev/pts dev; do
  if grep -q " $R/$m " /proc/mounts; then
    umount "$R/$m" 2>/dev/null || umount -l "$R/$m"
  fi
done
echo "chroot da TOCAIA desmontado."
