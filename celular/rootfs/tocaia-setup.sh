#!/bin/bash
# Roda DENTRO do Debian do celular, como root, uma vez, ao fim da instalação.
#   bash /opt/tocaia/tocaia-setup.sh analista
set -e
USUARIO="${1:-analista}"

# trem no PATH e saudação em todo shell
chmod +x /usr/local/bin/trem /usr/local/bin/tocaia-papel-de-parede
chmod 644 /etc/profile.d/tocaia.sh

# Android só deixa usar a rede quem está nestes grupos (paranoid networking).
# Sem isso, no modo chroot (root) o usuário analista fica sem internet.
groupadd -g 3003 aid_inet 2>/dev/null || true
groupadd -g 3004 aid_net_raw 2>/dev/null || true
groupadd -g 1015 aid_sdcard_rw 2>/dev/null || true

# usuário do dia a dia (o tema vem do /etc/skel gerado pelo gerar_tema.py)
if ! id "$USUARIO" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$USUARIO"
fi
usermod -aG sudo,aid_inet,aid_net_raw,aid_sdcard_rw "$USUARIO"
# celular é de uma pessoa só: sudo sem senha para o analista
echo "$USUARIO ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/tocaia
chmod 440 /etc/sudoers.d/tocaia

# venvs das tools sob demanda podem ser criados pelo analista
mkdir -p /opt/tocaia/venvs && chown -R "$USUARIO" /opt/tocaia/venvs

# pt-BR e fuso de São Paulo
if [ -f /etc/locale.gen ]; then
  sed -i 's/^# *pt_BR.UTF-8/pt_BR.UTF-8/' /etc/locale.gen
  locale-gen >/dev/null
  update-locale LANG=pt_BR.UTF-8 || true
fi
ln -sf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime
echo "America/Sao_Paulo" > /etc/timezone

# marca a edição (o trem e o manifesto podem ler)
cat > /etc/tocaia-release <<'EOF'
NOME="TOCAIA OSINT Linux"
VERSAO="1.0"
CODINOME="Matula"
EDICAO=android
BASE="Debian trixie (proot-distro)"
EOF

update-desktop-database /usr/share/applications 2>/dev/null || true
echo "TOCAIA Matula: usuário $USUARIO pronto."
