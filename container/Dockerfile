# TOCAIA OSINT Linux — variante leve (container / WSL), base Alpine.
# Build a partir da raiz do repositório:
#   docker build -f container/Dockerfile -t tocaia:tropeiro .

FROM alpine:3 AS build
RUN apk add --no-cache python3
WORKDIR /src
COPY build.py catalogo.json ./
COPY tools/ tools/
RUN python3 build.py

FROM alpine:3
LABEL org.opencontainers.image.title="TOCAIA OSINT Linux" \
      org.opencontainers.image.description="Distro OSINT leve, menu pelas fases da TOCAIA" \
      org.opencontainers.image.source="https://github.com/Ridd1kulusC0d3r/TOCAIALinux" \
      org.opencontainers.image.licenses="MIT"
# py3-pip traz o ensurepip que o trem usa para criar os venvs sob demanda
RUN apk add --no-cache python3 py3-pip ca-certificates git \
 && adduser -D -s /bin/sh analista
COPY --from=build /src/dist/ /opt/tocaia/dist/
COPY catalogo.json /opt/tocaia/
COPY trem/trem.py /usr/local/bin/trem
COPY container/tocaia-profile.sh /etc/profile.d/tocaia.sh
COPY wargames/ /opt/tocaia/wargames/
RUN chmod +x /usr/local/bin/trem \
 && mkdir -p /opt/tocaia/venvs && chown -R analista /opt/tocaia/venvs
ENV TREM_HOME=/opt/tocaia
USER analista
WORKDIR /home/analista
ENTRYPOINT ["trem"]
