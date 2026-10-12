# War games ataque × defesa — "Tropeiro × Atalaia"

Um jogo de purple team em que **o vermelho (Tropeiro)** executa técnicas reais do MITRE ATT&CK e **o azul (Atalaia)** tenta detectá-las com o Wazuh. O `trem placar` é o juiz: lê o cenário e os alertas do Wazuh e diz quem pontuou em cada passo.

```
cenário (JSON) ──┐
                 ├──> trem placar ──> vencedor · cobertura % · MTTD · lacunas
alerts.json ─────┘         │
                           └─ passos com "deteccao": "ausencia" usam o silêncio do host
```

## Regras

| Situação | Quem pontua |
|---|---|
| Alerta com a mesma técnica ATT&CK (ou regra listada no passo), no host certo, dentro da janela | **azul**: pontos do passo + bônus de rapidez (até 50%) |
| Nenhum alerta que bata | **vermelho**: pontos do passo |
| Passo de limpeza de rastro (`"deteccao": "ausencia"`) e o host alvo silenciou enquanto os outros falavam | **azul** (detecção pela ausência) |

`aceitar_tecnica_pai: true` faz um alerta de `T1059.001` valer para um passo `T1059.003`. Desligue para placar mais rigoroso.

## Três jeitos de jogar

1. **Sem laboratório (agora, em 1 minuto):** dados sintéticos.
   ```
   trem placar wargames/cenarios/rodada1-tropeiro-x-atalaia.json wargames/demo/alerts-demo.json
   trem silencio wargames/demo/alerts-demo.json
   ```
2. **Laboratório local:** Wazuh oficial em Docker + duas VMs com agente.
   ```
   sh wargames/lab/subir-lab.sh v4.X.Y        # versão em github.com/wazuh/wazuh-docker/releases
   ```
   No Windows alvo, com o Atomic Red Team instalado (Invoke-AtomicRedTeam), o vermelho roda cada passo no horário do cenário, por exemplo `Invoke-AtomicTest T1059.001 -TestNumbers 1`. No Linux alvo, `Invoke-AtomicTest T1136.001` via PowerShell Core.
   Ao fim: `sh wargames/lab/exportar-alertas.sh` e `trem placar cenario.json alerts.json --relatorio placar.md`.
3. **Na nuvem grátis:** abra `nuvem/TOCAIA_Colab.ipynb` no Colab e suba seu `alerts.json`.

## Ciclo do jogo

1. Jogar a rodada → 2. Placar mostra as **lacunas** → 3. Azul escreve regra (Sigma → Wazuh) → 4. Rejogar o mesmo cenário → 5. A cobertura sobe. Cada rodada vira um post e uma regra publicada.

## Escrevendo um cenário

```json
{"id": "P7", "nome": "Movimento lateral por SMB", "tecnica": "T1021.002",
 "alvo": "win-lab-02", "quando": "2026-10-12T16:00:00-03:00", "pontos": 20,
 "regras": ["ID_DA_SUA_REGRA"], "janela_s": 900}
```
`regras` é opcional (IDs de regra do Wazuh que também valem). `quando` precisa bater com o horário em que o vermelho executou.

## Ética e segurança do laboratório

Só em máquinas suas, isoladas, sem dados reais. Técnicas de ataque **nunca** fora do laboratório. Os alertas da pasta `demo/` são sintéticos e os IDs 1009xx são fictícios.
