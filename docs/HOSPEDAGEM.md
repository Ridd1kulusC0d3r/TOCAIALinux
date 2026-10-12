# Hospedagem da ISO e dos artefatos pesados

A ISO da TOCAIA pesa ~1,3 GB. Isto não cabe no repositório git (limite de **100 MB por
arquivo**; Git LFS tem só 1 GB grátis e estoura rápido). Mas há caminhos grátis e bons.

## Primeiro: o GitHub já resolve (via Releases)

O limite de 100 MB é do **repositório**. O **GitHub Releases** aceita **até 2 GB por
arquivo**, de graça, ao lado do código. Para 1 ISO de ~1,3 GB, **basta**. Nosso CI
(`.github/workflows/build.yml`) já publica a ISO, o `.tar.gz` do WSL e os `.sha256` como
assets do Release a cada tag `v*`. A imagem de container vai para o **GHCR** (GitHub
Packages), também grátis.

## Além do GitHub (espelhos e banda grátis)

| Opção | Por que usar | Limite / custo |
|---|---|---|
| **Internet Archive** (archive.org) | permanente; link direto **+ `.torrent` automático**; combina com a cadeia de custódia | grátis, generoso |
| **Cloudflare R2** | **egress grátis** (download não paga banda) + domínio próprio | 10 GB grátis |
| **SourceForge** | rede de **mirrors** mundial + torrent + estatísticas de download | grátis, ilimitado |
| **OSUOSL / FossHub** | mirrors dedicados a projetos open-source (hospedam várias distros) | grátis (mediante pedido) |
| **Backblaze B2** | barato; egress grátis via aliança CDN Cloudflare | 10 GB grátis |
| **Torrent / IPFS** | distribui a banda entre quem baixa; resiliente | grátis |

### Recomendação para a TOCAIA

1. **GitHub Releases** — origem (já automatizado).
2. **Internet Archive** — espelho permanente + torrent; publique o `.iso`, o `.sha256` e o `.torrent`.
3. Se crescer: **SourceForge/OSUOSL** (mirrors) e **Cloudflare R2** (domínio de download sem pagar banda).

Sempre publique o **SHA-256** junto do arquivo, em todo mirror. É a mesma lógica do
`trem manifesto`: quem baixa confere a integridade antes de gravar.

## Subir ao Internet Archive pelo CI (opcional, atrás de secrets)

O job `arquivo` em `.github/workflows/build.yml` sobe a ISO ao Internet Archive **se**
os secrets existirem (do contrário é pulado, sem quebrar o build). Configure uma vez:

1. Crie uma conta em https://archive.org e pegue as chaves S3 em
   https://archive.org/account/s3.php
2. No repositório: *Settings → Secrets and variables → Actions* e adicione:
   - `IA_ACCESS_KEY` e `IA_SECRET_KEY`
3. A cada tag `v*`, o CI publica em `https://archive.org/details/tocaia-osint-linux-<tag>`
   com o `.iso`, o `.sha256` e o `.torrent` que o Archive gera sozinho.

Localmente, o mesmo pode ser feito com a CLI `ia`:

```
pip install internetarchive
ia configure            # usa as chaves S3
ia upload tocaia-osint-linux-v1.0 dist/*.iso dist/*.sha256 \
   --metadata="title:TOCAIA OSINT Linux 1.0 Tropeiro" \
   --metadata="mediatype:software" --metadata="language:por"
```

O Internet Archive gera o `.torrent` automaticamente para o item — divulgue esse link
junto do Release para distribuir a banda.
