# TOCAIA "Matula" — a edição Android (guia completo)

> A matula é a sacola de comida que o tropeiro leva na viagem.
> A "Matula" é a TOCAIA que cabe no bolso: o mesmo `trem`, o mesmo tema e o mesmo menu pelas fases, rodando no celular.

Aparelho de referência: **POCO X6 Pro 5G** (codinome `duchamp`, MediaTek Dimensity 8300-Ultra, HyperOS).
Funciona em praticamente qualquer Android 10+ com processador ARM 64 bits.

---

## 1. A engenharia reversa do "modo DeX"

O Samsung DeX é software fechado, preso à One UI. Não dá para copiar o código dele, e nem faria sentido.
O que dá é **decompor o que ele faz** e recriar cada peça com peças abertas:

| Peça do DeX | O que ela faz | Peça aberta na Matula |
|---|---|---|
| Sistema de desktop | menu iniciar, barra, área de trabalho | **Debian 13 + Xfce**, com o tema e o menu por fases da TOCAIA |
| Servidor de janelas | desenha o desktop numa tela | **Termux:X11** (app Android) |
| Janelas redimensionáveis | apps Android em janelas soltas | **janelas livres (freeform)** do próprio Android, ligadas pelo `tocaia_pc.py preparar` |
| Saída para tela grande | cabo USB-C → monitor | **celular**, **PC** (monitor virtual do scrcpy) ou **TV** (Miracast) |

### Por que não tem cabo

O DeX clássico depende de *DisplayPort Alt Mode* na porta USB-C. A linha POCO X usa USB-C 2.0, sem saída de vídeo:
a própria Xiaomi documenta isso no irmão mais novo, o [POCO X7 Pro](https://www.mi.com/ph/support/faq/details/KA-528066/).
Nenhum adaptador USB-C → HDMI vai funcionar no X6 Pro. Os caminhos que funcionam são os três desta edição.

### A peça que mais se parece com o DeX: o monitor virtual do scrcpy

Desde a versão 3.0, o [scrcpy](https://github.com/Genymobile/scrcpy) consegue **criar um monitor virtual** dentro do Android e mostrar só ele numa janela do PC.
A tela do celular continua livre. É exatamente a experiência do DeX: o desktop num monitor, o celular na mão.
A versão 4.0 (maio/2026) deixou esse monitor **redimensionável como uma janela de PC** ([fonte](https://ubuntuhandbook.org/index.php/2026/05/scrcpy-4-0-resizable-virtual-display/)).
O `tocaia_pc.py dex` usa isso e abre o Termux:X11 direto dentro do monitor virtual.

---

## 2. As duas modalidades

| | **Modalidade A — Tudo no celular** | **Modalidade B — Telas externas** |
|---|---|---|
| Onde aparece | na tela do próprio POCO | no PC (janela) ou na TV |
| Precisa de | só o celular (teclado/mouse Bluetooth recomendados) | PC com adb + scrcpy, ou TV com Miracast |
| Como abre | botão **TOCAIA Desktop** na tela inicial | botão **TOCAIA Desktop** no celular + dois cliques em **TOCAIA-DeX** no PC; ou botão **TOCAIA na TV** |
| Para quê | campo, viagem, sem nada além do bolso | trabalho longo, apresentação, aula, palestra |

As duas usam **o mesmo Debian instalado**. Você não instala duas vezes.

---

## 3. As três formas de instalar

| | **1. Sem root** (padrão) | **2. Com root** | **3. Sistema novo** |
|---|---|---|---|
| Mexe no sistema do celular? | não | sim (bootloader desbloqueado + Magisk/KernelSU) | sim, troca o HyperOS |
| Apaga os dados? | não | **sim**, ao desbloquear | **sim** |
| Desempenho | bom (o proot traduz chamadas) | melhor (chroot direto) | o melhor, sem bloatware |
| Apps de banco | funcionam | podem detectar e bloquear | podem detectar e bloquear |
| Garantia | intacta | em risco | em risco |
| Recomendado para | **começar hoje** | quem já usa o sem-root e quer velocidade | celular dedicado a investigação |

### 3.1 Sem root (proot) — comece por aqui

1. Instale três apps **fora da Play Store** (as versões da Play estão defasadas):
   - **Termux** — [F-Droid](https://f-droid.org/packages/com.termux/) ou [GitHub](https://github.com/termux/termux-app/releases)
   - **Termux:X11** — APK `termux-x11-universal-debug.apk` da tag *nightly* em [termux-x11/releases](https://github.com/termux/termux-x11/releases)
   - **Termux:Widget** — mesma origem do Termux (para os botões na tela inicial)
   - **Termux:API** — opcional, mesma origem
2. Abra o Termux e cole:
   ```
   curl -fsSL https://raw.githubusercontent.com/Ridd1kulusC0d3r/TOCAIALinux/main/celular/instalar.sh | bash
   ```
3. Espere. Baixa uns **1 a 1,5 GB** (Debian + Xfce + Firefox + base OSINT). Use Wi-Fi.
4. Na tela inicial: segure num espaço vazio → **Widgets** → **Termux:Widget** → arraste. Aparecem os botões TOCAIA.
5. Toque em **TOCAIA Desktop**.

O que o instalador faz, passo a passo (rode `python ~/TOCAIALinux/celular/tocaia_celular.py instalar --simular` para ver sem executar):

```
pkg install x11-repo termux-x11-nightly proot-distro python
proot-distro install debian                     # Debian 13 "trixie"
apt-get install <a MESMA lista de pacotes da ISO, menos o que é de pendrive>
copia trem, tools .pyz, war game, tema e menu por fases para /opt/tocaia
cria o usuário analista, pt-BR, fuso de São Paulo
grava a ficha do aparelho (cadeia de custódia)
```

### 3.2 Com root (chroot) — o mesmo Debian, mais rápido

O chroot usa **o mesmo Debian** que o proot-distro baixou. Você pode ter os dois e escolher na hora:
o botão **TOCAIA Desktop (root)** entra por chroot, o **TOCAIA Desktop** entra por proot.

O que muda por dentro (`celular/chroot/entrar-chroot.sh`):
- monta `/dev`, `/proc`, `/sys`, `/sdcard` e a `/tmp` do Termux (onde mora a tela `:0` do Termux:X11);
- o usuário `analista` entra nos grupos `aid_inet` (3003) e `aid_net_raw` (3004): sem isso o Android bloqueia a rede de quem não é root no chroot;
- cria um `resolv.conf`, porque o Android não tem um.

**Para ter root no X6 Pro você precisa desbloquear o bootloader.** Requisitos atuais da Xiaomi para aparelhos Global
([guia de out/2025](https://www.gizchina.com/editorial/how-to-unlock-the-bootloader-on-xiaomi-hyperos-global-devices)):

- só aparelhos **Global** (modelos China ficam de fora);
- conta Xiaomi com **30 dias ou mais**;
- pedido de permissão pelo app **Xiaomi Community** (região Global); se bater o limite diário, tente depois da meia-noite no horário da China;
- vincular a conta em *Opções do desenvolvedor → Status do Mi Unlock*, **usando dados móveis**, com chip físico;
- espera típica de **72 horas** (pode ser mais); nesse período não troque conta, chip nem resete;
- **1 aparelho por conta por ano**;
- o desbloqueio **apaga tudo**.

Depois do desbloqueio, o root é feito com **Magisk** ou **KernelSU** corrigindo a imagem de boot do *mesmo* firmware que está no celular
(aparelhos que saíram com Android 13+ costumam usar `init_boot.img`; confira dentro do pacote do firmware).

> ⚠️ **Anti-rollback da Xiaomi:** nunca grave um firmware **mais antigo** que o atual pelo fastboot. Pode travar o aparelho de vez.
> Baixe o firmware fastboot exatamente da versão que você está usando.

### 3.3 Sistema novo — trocar o HyperOS

Pesquisa de outubro/2026 para o `duchamp`:

| Opção | Situação | Para quem | Observação |
|---|---|---|---|
| **Evolution X** | builds marcadas como oficiais ([thecustomrom](https://thecustomrom.com/devices/xiaomi/duchamp), verificado em out/2026) | quem quer Android limpo e rápido | a página diverge entre Android 16 e 17; confira no site da ROM |
| **Lunaris AOSP** | builds marcadas como oficiais, Android 16 (mesma fonte) | idem | |
| **/e/OS** | **não oficial**, mantida por um usuário; 3.1.1 (set/2025) até 4.2 (ago/2026) ([fórum /e/](https://community.e.foundation/t/unofficial-build-poco-x6-pro-duchamp-for-e-os-a15-3-1-1/74657)) | **OPSEC**: sem serviços do Google por padrão | não oficial = sem garantia de atualização |
| **GSI** (imagem genérica Treble) | possível em tese; sem relato confiável para o duchamp | laboratório | câmera, 5G e sensores costumam falhar |
| **Linux nativo** (postmarketOS, Droidian, Ubuntu Touch) | **não achei port** para o Dimensity 8300 | — | não recomendado hoje |

**A recomendação da TOCAIA para "sistema novo":** em vez de uma ROM "TOCAIA" (que exigiria compilar e manter um Android inteiro),
use **Evolution X ou Lunaris + root + a Matula em modo chroot**. A TOCAIA vira a camada de investigação por cima de um Android limpo.
Para um **celular dedicado só a investigação**, o /e/OS é o que mais conversa com a doutrina (menos telemetria), aceitando o risco de ser não oficial.

Passos gerais (variam por ROM; siga sempre o guia oficial de cada uma):
1. Desbloquear o bootloader (seção 3.2).
2. Atualizar o HyperOS para a versão de firmware que a ROM pede.
3. Gravar a recovery da ROM pelo fastboot.
4. *Format data* e instalar a ROM pela recovery (`adb sideload`).
5. Root (Magisk/KernelSU), Termux e o `instalar.sh` da Matula.

---

## 4. As três telas

### No celular (modalidade A)
- Toque em **TOCAIA Desktop**. O app Termux:X11 abre com o Xfce da TOCAIA.
- Teclado e mouse **Bluetooth** transformam o celular num mini-PC. Sem eles, o toque funciona como mouse (toque = clique, dois dedos = clique direito).
- Ajustes da tela do Termux:X11 (resolução, tela cheia, teclado extra): pela tela **Preferences** do app, ou no Termux com
  `termux-x11-preference "fullscreen"="false" "showAdditionalKbd"="true"` (com o app aberto).

### No PC (modalidade B) — o "DeX" de verdade
Uma vez só:
1. No celular: *Configurações → Sobre o telefone →* toque 7× em **Versão do SO** → *Opções do desenvolvedor* → ligue **Depuração USB**
   (no HyperOS, ligue também **Depuração USB (Configurações de segurança)**).
2. No PC: instale **Python 3**, **adb** e **scrcpy 3.0+** (o menu `checar` mostra o comando de cada sistema).
3. Conecte o cabo e dois cliques em `celular/pc/TOCAIA-DeX (Windows).bat` (ou `.command` no Mac, `.sh` no Linux) → **2. preparar**.

No dia a dia:
1. No celular, toque em **TOCAIA Desktop**.
2. No PC, dois cliques em **TOCAIA-DeX** → **3. abrir o desktop TOCAIA no PC**.
3. Abre uma janela "TOCAIA · Matula" de 1920×1080. No scrcpy 4.0+, dá para redimensionar.

Sem cabo (Android 11+): *Opções do desenvolvedor → Depuração sem fio → Parear com código* e
`python3 tocaia_pc.py parear IP:PORTA CODIGO`, depois `python3 tocaia_pc.py conectar IP:PORTA`.

### Na TV (modalidade B)
- Toque em **TOCAIA na TV**. O desktop abre e o Android mostra a tela de **Transmitir**: escolha a TV.
- Precisa de TV ou adaptador com **Miracast** (no HyperOS aparece como *Transmitir*). Chromecast puro não recebe Miracast.
- É espelhamento: a TV mostra o que está na tela do celular. Gire o celular para paisagem.

---

## 5. Requisitos básicos (POCO X6 Pro)

| Item | Mínimo | Ideal |
|---|---|---|
| Espaço livre | 3 GB | 6 GB (sobra para venvs e casos) |
| RAM | 8 GB (o X6 Pro tem 8 ou 12) | 12 GB |
| Android | 10 | o HyperOS mais recente do seu modelo |
| Acessórios | nenhum | teclado + mouse Bluetooth |
| Para o modo PC | Python 3, adb, scrcpy 3.0 | scrcpy 4.0 (janela redimensionável) |
| Para o modo TV | TV com Miracast | — |

---

## 6. Inovação: a ficha do aparelho na cadeia de custódia

O `trem manifesto` já registrava o hash de cada ferramenta. Na Matula, ele registra também **o aparelho de coleta**:
fabricante, modelo, codinome, versão do Android, build do HyperOS, **patch de segurança**, `verifiedbootstate` e se o **bootloader está travado**.

Por que isso importa: numa perícia, a defesa pode questionar a integridade do dispositivo usado na coleta.
Um celular com bootloader destravado ou patch antigo é um fato que precisa estar no laudo, não uma surpresa no tribunal.
Se qualquer item mudar (por exemplo, você destravou o bootloader), **o ID do manifesto muda**, e `trem manifesto --verificar` aponta:
*"aparelho de coleta: diferente"*.

Tudo em Python simples: `subprocess` lê o `getprop` do Android, `json` grava a ficha e `hashlib` entra no ID do manifesto.

---

## 7. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| O desktop fecha sozinho depois de uns minutos | o Android 12+ mata processos filhos ("phantom process killer") | `tocaia_pc.py preparar` (uma vez) e tire o Termux da economia de bateria: *Configurações → Apps → Termux → Economia de bateria → Sem restrições* |
| Tela preta com só o cursor | modo de desenho do Termux:X11 | abra com `tocaia_celular.py desktop --legacy` (passa `-legacy-drawing` ao Termux:X11) |
| Cores trocadas (azul vira laranja) | formato de cor | abra com `tocaia_celular.py desktop --bgra` (passa `-force-bgra`) |
| `TOCAIA Desktop (root)`: sem internet no Debian | grupo de rede do Android | rode de novo `bash /opt/tocaia/tocaia-setup.sh analista` dentro do Debian |
| `scrcpy` abre o celular inteiro, não o desktop | scrcpy antigo | atualize para 3.0+ (`tocaia_pc.py checar`) |
| Janela do PC preta | o desktop não estava aberto no celular | toque em **TOCAIA Desktop** antes do **TOCAIA-DeX** |
| `adb devices` mostra `unauthorized` | chave do PC não aceita | desbloqueie o celular e aceite o aviso "Permitir depuração USB" |
| A TV não aparece em Transmitir | TV sem Miracast, ou Wi-Fi diferente | mesma rede; verifique se a TV aceita "Screen Mirroring/Miracast" |
| Pouco espaço | Debian + Firefox ~1,5 GB | `proot-distro login debian -- apt-get clean` |

Diagnóstico rápido: `python ~/TOCAIALinux/celular/tocaia_celular.py doutor` (no celular) e `python3 tocaia_pc.py checar` (no PC).

---

## 8. Ética

A Matula é a mesma TOCAIA, com as mesmas regras: **fonte aberta, sem invadir, sem enganar, sem assediar**.
Celular de investigação também é OPSEC: use um aparelho e contas separados do seu pessoal e confira `trem opsec` antes de coletar.
