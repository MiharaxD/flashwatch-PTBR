# Contexto do projeto — FlashWatch PT-BR

Resumo para retomar o trabalho rápido (pessoas ou agentes). Os detalhes estão
nos documentos indicados; aqui fica o mapa.

## O que é

Overlay para Windows que acompanha as recargas de **feitiços de invocador e
ultimates inimigos** de League of Legends lendo o **chat do jogo por OCR**.
Só observa pixels da tela: não injeta, não lê memória, não toca em arquivos do
jogo, não envia entradas. Rede apenas para o Data Dragon (Riot) e para o
GitHub (atualizações).

- **Este repositório:** `MiharaxD/flashwatch-PTBR` (remote `origin`).
- **Projeto original:** `abenfraj/flashwatch` (remote `upstream`), MIT.
  Fork baseado no commit `5193229`. Ver `NOTICE-PTBR.md` e `LICENSE`.
- **Versão atual:** `1.0.8` (`src/version.py`), identidade visual "Hextech".
- **Idiomas:** francês, inglês e português brasileiro (`pt_BR`). O padrão
  inicial é inglês; o usuário escolhe na primeira tela do guia.

> O `CLAUDE.md` é a **especificação original** do upstream. A implementação já
> vai além dela (ultimates, funções/lanes, chamadas do time, atualizador,
> instalador) e diverge em alguns pontos — ex.: usa **Python 3.11**, não 3.13,
> porque o `rapidocr-onnxruntime` não tem wheels para todas as versões novas.

## Fluxo principal

```
GameDetector (janela RiotWindowClass / processo)
   ↓
CaptureWorker (thread própria, mss a cada 200 ms)
   ↓ FrameDiffer: pula quadros sem mudança nos glifos
chat_detector: acha o chat pelos timestamps "(mm:ss)", sem coordenadas fixas
   ↓
OcrEngine: segmentação de linhas com OpenCV (duas máscaras) + RapidOCR por linha,
           com cache por hash exato da linha
   ↓
MessageParser: texto → SpellEvent ("Ahri usou Flash", "Aguarde ... - 245 seg.",
               pings "Nasus R", chamadas do time "jg flash 950")
   ↓ fila (queue) — a thread de captura nunca toca no Qt
Application._drain_results (timer Qt, 50 ms)
   ↓
TimerManager: deduplicação (campeão|feitiço|mm:ss), priming, correção pelo
              relógio do jogo, detecção de nova partida
   ↓
Overlay (transparente, click-through, sempre no topo) + Notifier (áudio)
```

Regras de confiabilidade importantes (detalhes no `README.md`, seção
"Why it is reliable"):
- Um timer em andamento **não é alterado** por leituras que diriam o mesmo ou
  menos tempo; só um recast (+15 s) ou um uso **confirmado** sobre um timer
  apenas inferido pode substituí-lo.
- Eventos incertos (pings sem "usou", chamadas digitadas) mostram um `?` no
  ícone do feitiço.
- O fim de partida é lido pelo **processo**, não pela janela (alt-tab e telas
  de carregamento não zeram os timers).

## Mapa do código (`src/`)

| Módulo | Papel |
| --- | --- |
| `main.py` | `Application`: inicialização, bandeja, threads, atalhos, atualização, troca de idioma, modo demo, teste |
| `ocr.py` | `CaptureWorker`, `OcrEngine`, `FrameDiffer`, cor do nome (inimigo = vermelho), zonas extras (relógio, placar, carregamento) |
| `chat_detector.py` | Região do chat a partir das linhas com timestamp |
| `message_parser.py` | Texto OCR → `SpellEvent`; tolerância a erros de OCR; formatos PT-BR (`usou`, `Aguarde/Espere`) |
| `timer_manager.py` | `ActiveTimer`, `TimerManager`: estado, dedupe, relógio, roles, demo |
| `cooldowns.py` | Tabela de recargas, Insight Cósmico/Botas Jônicas, normalização de nomes |
| `riot_assets.py` | Data Dragon (`championFull.json`, `summoner.json`, ícones), cache por versão/locale |
| `role_reader.py`, `roles.py` | Lanes inimigas lidas da tela de carregamento/placar; aliases de lanes digitados pelos jogadores |
| `overlay.py` | Overlay com 3 layouts: barra (horizontal/vertical), cartões, lista |
| `zone_overlay.py` | Modo teste: moldura para posicionar à mão as zonas chat/relógio/placar/carregamento |
| `ui.py` | Janela de controle (porte literal das maquetes `design/maquette/Flashwatch *.dc.html`) |
| `onboarding.py` | Guia de configuração de 8 telas desenhado com QPainter (porte das maquetes "Onboarding") |
| `hextech.py`, `theme.py`, `icons.py` | Identidade visual: botões/painéis Hextech, paletas, ícones desenhados em código |
| `i18n.py` | Catálogo único de textos FR/EN/PT (`tr(key)`) |
| `settings.py` | `settings.json` em `assets/` (fallback `%LOCALAPPDATA%/Flashwatch`); migração entre versões |
| `audio.py` | Sons sintetizados em WAV, tocados via `winsound` |
| `updater.py` | Releases do GitHub `MiharaxD/flashwatch-PTBR`, download com SHA-256, troca por renomeação |
| `autostart.py`, `single_instance.py` | Iniciar com o Windows (chave Run); uma instância só (mutex) |
| `self_test.py` | Botão Teste: roda a cadeia inteira sobre `resources/test/chat-sample.png` |
| `version.py` | `__version__` |

## Outras pastas

- `tests/` — scripts independentes (`test_*.py`), cada um sai com código ≠ 0 se
  falhar. Fixtures PT-BR offline em `tests/fixtures/pt_BR/`.
- `tools/` — `run_tests.py` (roda tudo, logs em `build/test-results`),
  `diagnose.py` (coleta amostras de OCR numa partida), `release_meta.py`,
  `verify_installer.py`, geradores de marca/SEO/arte.
- `resources/` — fontes (Beaufort, Spiegel, Mulish), artes, marca, amostra do
  autoteste. Vai dentro do executável.
- `design/` — kit de direção de arte e maquetes HTML (em francês). Não entra no
  executável.
- `docs/` — documentação de cada revisão PT-BR (em português).
- `site/` — página de download (Vercel). Lê as releases pela API do GitHub.
- `assets/`, `build/`, `dist/`, `.venv/` — gerados localmente, ignorados pelo git.

## Comandos

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller

.\.venv\Scripts\python.exe src\main.py           # rodar (ou run.bat)
.\.venv\Scripts\python.exe tools\run_tests.py    # todos os testes (Qt offscreen)
.\.venv\Scripts\python.exe tests\test_ptbr.py    # uma suíte
.\.venv\Scripts\python.exe build.py              # dist/FlashWatch-PTBR.exe
.\.venv\Scripts\python.exe build_installer.py    # MSI por usuário
.\.venv\Scripts\python.exe tools\diagnose.py --locale pt_BR --seconds 120
```

## Release e atualização

- `.github/workflows/release.yml`: push na `main` que altera o app → testes
  (exceto `test_ocr_performance.py`), bump de versão, build no Windows, release
  no GitHub. Mudanças só em `*.md`, `site/`, `design/`, `.github/` não geram
  versão.
- Commits com **`[skip release]`** na mensagem não disparam release. Os commits
  recentes usam isso e mensagens em português.
- O atualizador exige o asset **`FlashWatch-PTBR.exe`** na release.
- **Atenção:** `build_installer.py` tem fixos o caminho
  `dist/hextech-1.0.8/FlashWatch-PTBR.exe` e o `APP_SHA256` desse executável.
  Em cada nova versão é preciso atualizar os dois, senão o MSI não é gerado.

## Convenções

- Comentários e docstrings explicam o **porquê**, em inglês, em prosa longa;
  documentação nova da edição PT-BR fica em `docs/` em português.
- Textos da interface sempre via `i18n.tr()`, com as três colunas preenchidas.
- IDs canônicos não são traduzidos: `MonkeyKing`, `SummonerFlash`, `Flash`,
  `ULT`, `JUNGLE`. Só os aliases e nomes exibidos vêm do locale.
- `ui.py` e `onboarding.py` seguem as maquetes pixel a pixel; medidas vêm de lá.
- Cooldowns **não** foram rebalanceados no fork; não preencher valores adivinhados.
- Não promover hipóteses do parser a "formato real" sem captura do cliente.

## Limitações conhecidas

- Detecção automática do chat validada só em quadros sintéticos; numa captura
  brasileira real escolheu a área errada (o modo teste permite posicionar à mão).
- `Aguarde/Espere ... - N seg.` em PT-BR são **hipóteses** sem captura real.
- O executável empacotado 1.0.8 não foi testado dentro de uma partida.
- `test_ocr_performance.py` está no limite (917 ms para teto de 900 ms em uma
  verificação).
- Executável sem assinatura digital (aviso do SmartScreen).
- Jogar em modo **sem bordas**; tela cheia exclusiva não é capturada.

## Onde ler mais

- `README.md` — documentação técnica completa (inglês).
- `docs/PTBR.md` — arquitetura da localização e evidências do parser.
- `docs/VALIDACAO-PTBR.md`, `docs/CORRECOES-R-GUIA.md` — resultados e limites.
- `docs/IDENTIDADE-HEXTECH.md` — revisão visual 1.0.8.
- `docs/ATUALIZACOES-AUTOMATICAS.md`, `docs/INSTALADOR.md` — distribuição.
- `docs/CARTOES-*.md`, `docs/ICONES-DE-RECARGA.md` — evolução do layout de cartões.
- `RELEASE_NOTES.md` — notas da versão atual.
