# =============================================================================
# TOCAIA OSINT Linux — edição container/WSL (base Alpine, a mais leve)
#
# Imagem base ~8 MB; com Python e o essencial, fica na casa das dezenas de MB.
# Sem interface gráfica: é a TOCAIA de linha de comando, universal, para Docker,
# WSL, Raspberry Pi e nuvem. As ferramentas .pyz (stdlib) rodam direto; as de
# terceiro entram sob demanda pelo `trem`, cada uma em seu venv.
#
# Build (multi-arquitetura):
#   docker buildx build --platform linux/amd64,linux/arm64 \
#       -f edicoes/alpine/Dockerfile -t tocaia:1.0 --load .
# Uso:
#   docker run --rm -it tocaia:1.0            # abre o shell com a saudação
#   docker run --rm tocaia:1.0 relogio --demo # roda uma ferramenta direto
# =============================================================================
FROM alpine:3.20

# Ferramentas de sistema que valem pré-instalar (passivas e leves).
# py3-virtualenv dá o venv sem depender do ensurepip (que falta no Alpine).
RUN apk add --no-cache \
        python3 py3-pip py3-virtualenv \
        git ca-certificates curl bind-tools whois exiftool \
        bash less jq tzdata \
    && update-ca-certificates \
    && cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
    && echo "America/Sao_Paulo" > /etc/timezone

# Marca a edição (o trem lê isto para dar dicas de 'apk add' etc.)
RUN mkdir -p /opt/tocaia && cat > /etc/tocaia-release <<'EOF'
NOME="TOCAIA OSINT Linux"
VERSAO="1.0"
CODINOME="Tropeiro"
EDICAO=alpine
BASE="Alpine 3.20"
EOF

# Material da TOCAIA
COPY catalogo/catalogo.json      /opt/tocaia/catalogo.json
COPY ferramentas/*.pyz           /opt/tocaia/ferramentas/
COPY casos                       /opt/tocaia/casos
COPY trem/trem.py                /usr/local/bin/trem
COPY edicoes/alpine/tocaia-entrada /usr/local/bin/tocaia-entrada
COPY docs/manual                 /opt/tocaia/manual
COPY COMECE-AQUI.md              /opt/tocaia/COMECE-AQUI.md

RUN chmod +x /usr/local/bin/trem /usr/local/bin/tocaia-entrada \
    && ln -sf /usr/local/bin/trem /usr/local/bin/tocaia \
    && adduser -D -s /bin/bash analista \
    && mkdir -p /home/analista/casos \
    && cp -r /opt/tocaia/casos/. /home/analista/casos/ \
    && chown -R analista:analista /home/analista

# Saudação ao abrir o shell
RUN printf '%s\n' \
    'if [ -t 1 ] && [ -z "$TOCAIA_SAUDOU" ]; then export TOCAIA_SAUDOU=1; trem saudacao 2>/dev/null; fi' \
    > /etc/profile.d/tocaia.sh

ENV TOCAIA_HOME=/opt/tocaia LANG=pt_BR.UTF-8 PYTHONUNBUFFERED=1
USER analista
WORKDIR /home/analista

# Sem argumento: shell interativo. Com argumento: vira `trem <arg...>`.
ENTRYPOINT ["/usr/local/bin/tocaia-entrada"]
CMD ["--shell"]
