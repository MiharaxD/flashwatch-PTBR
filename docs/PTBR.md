# FlashWatch PT-BR

Localização de [abenfraj/flashwatch](https://github.com/abenfraj/flashwatch), baseada no commit `5193229865fbd4de266d9d9aff4ada6d8b2e2f77`. Escopo: idioma e compatibilidade com o cliente brasileiro. A licença MIT original está em `LICENSE`, sem alterações.

## Usar no Windows

Execute `dist/FlashWatch-PTBR.exe`. Não é necessário instalar Python. O primeiro uso precisa de internet para os dados e ícones da Riot; o cache e as configurações continuam na pasta `assets`, ao lado do programa, com o fallback original para `%LOCALAPPDATA%/Flashwatch`.

Na primeira tela do guia, escolha **Português / Brasil**. Nas configurações, a mesma opção aparece em **Client language / Idioma do cliente**. O padrão inicial inglês foi preservado, assim como configurações anteriores, inglês e francês. Jogue no modo de janela sem bordas, conforme o guia original.

Não foi publicada uma release deste trabalho. O executável local não tem assinatura digital. O atualizador mantém consulta, download sob ação do usuário, verificações e recuperação de falha, mas exige o arquivo **FlashWatch-PTBR.exe** na release para não substituir esta localização por um binário original sem português. O endereço continua sendo o repositório original; até uma publicação compatível existir, a consulta pode informar indisponibilidade. Nenhum endereço de fork foi inventado.

## Arquitetura analisada antes das alterações

| Componente | Responsabilidade existente | Adaptação |
| --- | --- | --- |
| `src/main.py` | Inicialização, bandeja, threads, troca de idioma e adoção dos dados | Saída explícita do loop após salvar, corrigindo o encerramento da build |
| `src/settings.py` | Configurações, migração, diretórios e padrões | Três locales documentados; contagem em 1,5× para novas configurações |
| `src/i18n.py` | Catálogo único FR/EN e formatação | Terceira coluna PT-BR, preservando os dois textos existentes |
| `src/ui.py` | Janela de controle com widgets Qt | Terceiro idioma e rótulos de funções separados de seus IDs |
| `src/onboarding.py` | Oito telas desenhadas com QPainter | Terceiro cartão no espaço existente, bandeira e validação do idioma |
| `src/riot_assets.py` | Data Dragon, cache por versão/locale e IDs canônicos | Fluxo original com `pt_BR`; tradução do nome genérico de fallback |
| `src/message_parser.py` | Texto OCR → eventos, índices oficiais, chamadas de jogadores | Verbo documentado, confusões sintéticas de OCR e hipóteses delimitadas |
| `src/cooldowns.py`, `src/roles.py` | Cooldowns, aliases e funções canônicas | Apenas aliases brasileiros; valores e IDs preservados |
| `src/ocr.py`, `src/chat_detector.py`, `src/game_detector.py` | Captura, segmentação, cache OCR e detecção | Apenas texto inicial localizado em `ocr.py`; algoritmos intactos |
| `src/timer_manager.py`, `src/overlay.py` | Estado dos timers e três exibições | PRONTO e medição do texto; hipótese de ping mantém indicador `?`; correção pontual da contagem invisível no tamanho padrão |
| `src/self_test.py` | Teste com captura real inglesa fornecida pelo upstream | Erro de imagem localizado; amostra original preservada |
| `src/updater.py`, `build.py`, workflow | Atualização e empacotamento | Nome do binário, mensagens localizadas e inclusão da licença |

Captura, frequência de leitura, cache de linhas, limites de threads, comparação de retratos, detecção do processo, áudio, atalhos, deduplicação, correção por relógio, configurações e formatos do overlay permanecem os existentes. A implementação não usa LCU, API de partida, memória do jogo, injeção ou automação de comandos no jogo. O aplicativo continua consultando os serviços que já usava: Data Dragon e GitHub para atualizações. As fontes complementares abaixo são referências de desenvolvimento, sem novos acessos durante o uso normal.

Na validação visual, você identificou que a barra mostrava ícones sem a contagem. O tamanho anterior de fonte (0,5×) media 6 pixels neste ambiente, mas uma trava antiga exigia 8 pixels para desenhar os números. A correção compara o espaço disponível à altura real da fonte, sem alterar o estado dos timers. Um teste reproduz a falha anterior e verifica os números após a correção.

Após seu pedido de legibilidade, o padrão para novas configurações passou a **1,5×**, três vezes o multiplicador anterior. A renderização foi conferida em áreas equivalentes a 1920×1080 e 2560×1440. O tamanho continua ajustável em Exibição; valores já salvos são respeitados. Não foi possível validar fisicamente um monitor 1440p nesta sessão.

O smoke também encontrou um processo sem janela após escolher sair. A build agora sai explicitamente do loop Qt com código 0, depois de parar a captura e salvar as configurações. Ocultar/fechar a janela continua com o comportamento original de minimizar para a bandeja; a correção afeta somente a ação de encerrar o programa.

## Dados oficiais e cooldowns

- [Documentação da Riot](https://developer.riotgames.com/docs/lol#data-dragon) confirma `pt_BR` e os caminhos por versão/idioma.
- O patch consultado foi `16.21.1`, retornado por `https://ddragon.leagueoflegends.com/api/versions.json`; ele não foi fixado no aplicativo.
- O carregador já usa `/cdn/{version}/data/{locale}/championFull.json`, contendo habilidades e ultimates de todos os campeões. Preservamos essa requisição única e o cache existente, sem trocar por uma requisição por campeão.
- Na preparação dos testes, os 173 IDs de `championFull.json` foram comparados com `champion.json`; a lista de habilidades de Ahri foi comparada com `champion/Ahri.json`. Os nomes dos feitiços vêm de `summoner.json`.
- `tests/fixtures/pt_BR/ddragon.json` contém campos selecionados desses dados oficiais, com URLs de origem. É uma fixture offline para testes, não um cadastro manual nem uma captura de partida. Q/W/E são mantidos nessa fixture para rastreabilidade; o programa continua usando somente as habilidades necessárias ao seu funcionamento original.
- Campeões, feitiços e ultimates exibidos são carregados da Riot. IDs como `MonkeyKing`, `SummonerExhaust`, `Flash`, `ULT` e funções como `JUNGLE` permanecem canônicos.
- Os cooldowns base e modificadores originais **não foram rebalanceados nem certificados como atuais**. Os dados do Data Dragon podem divergir do cliente; ultimates continuam com a estimativa original de nível e aceleração quando o chat não informa segundos. Nenhuma exceção foi preenchida com um valor adivinhado.
- [CommunityDragon](https://communitydragon.org/docs/assets) foi consultado como referência complementar. A [wiki](https://wiki.leagueoflegends.com/en-us/) bloqueou a leitura automatizada. Não houve evidência suficiente para justificar alteração de mecânicas ou cooldowns nesta localização.

## Evidências do parser

| Formato | Evidência / condição | Tratamento |
| --- | --- | --- |
| `Diana usou Flash`, `Jinx usou Flash` | Citados literalmente pela Riot nas [notas 25.17](https://www.leagueoflegends.com/pt-br/news/game-updates/patch-25-17-notes/), seção Relatório de Combate e rastreamento de Feitiços de Invocador | `usou` aceito; nomes resolvidos pelos índices oficiais |
| `<Campeão> usou <habilidade oficial>` | Generalização do formato acima; testes construídos com os nomes oficiais | Compatibilidade textual testada com os 173 nomes de ultimates e 11 feitiços carregados; não equivale a 184 capturas reais |
| `Nasus R` | Captura brasileira fornecida por você, preservada em `tests/fixtures/pt_BR/client-ultimate.png` | Resolve `R` para a ultimate oficial do alvo; mantém `?`, pois o ping não afirma uso |
| `<Campeão> usou R` | Formato informado por você; não aparece nessa captura | Resolve para `ULT`, com confirmação de uso; duração continua estimada quando não há segundos |
| `Espere por R - 33s`, `R - Pronto(a)` | Visíveis na mesma captura, mas sem campeão-alvo | Descartados; o campeão de quem enviou o ping não é usado como alvo inimigo |
| `us0u`, `Ahrl`, `Te1eporte`, acentos omitidos | Erros de OCR artificiais de teste | Tolerância restrita; não são frases documentadas do cliente |
| `Aguarde Ahri Flash - 245 seg.`, `Espere ... - 245 segundos` | **Hipóteses sem captura brasileira** | Apenas com dados `pt_BR`, nomes estritos, frase inteira, contagem de 1–600; evento incerto e indicador `?`. Também aceita `s`/`sec.` como variações sintéticas |
| `jg flash 950`, `selva exa 950`, `suporte ig 950` | Mensagens livres digitadas por jogadores, não anúncios do cliente | Fluxo original de chamadas; exige alvo, feitiço e horário; mantém `?` |
| `top sem flash`, `Ahri não usou Flash`, `Ahri abusou Flash` | Falsos positivos dos testes | Descartados |

Não habilitamos `utilizou` ou outros verbos apenas porque parecem traduções plausíveis. Uma frase capitalizada digitada por uma pessoa que reproduza exatamente o anúncio continua indistinguível do anúncio pelos pixels; essa é uma limitação do método original. Prefixos de autor, timestamp, confiança, filtros e demais regras originais são preservados para inglês e francês.

Nomes oficiais que começam com artigo, como a ultimate de Thresh, são comparados antes de descartar artigos. Isso evita interpretar o início de uma habilidade brasileira como um artigo inglês.

## Coletar amostras reais do cliente brasileiro

Agora há uma captura brasileira fornecida por você em `tests/fixtures/pt_BR/client-ultimate.png`, com proveniência e transcrição em `client-ultimate.json`. No recorte manual, o OCR reconheceu dois dos quatro pings `Nasus R`; os dois eventos foram resolvidos corretamente. A localização automática escolheu uma área errada nessa imagem, portanto a correção não certifica a detecção automática nem todos os textos da captura. Nenhuma partida aberta foi usada ou capturada nesta correção, conforme seu pedido.

A amostra do botão Teste, em `resources/test`, continua em inglês. Os testes da captura brasileira ficam no checkout e não são incorporados ao executável. Resultados desta revisão: `docs/CORRECOES-R-GUIA.md`.

Há duas maneiras locais de reunir evidências:

1. No aplicativo empacotado, escolha Português, entre em uma partida de treino, abra **Ajuda → Enquadrar chat** e confira as linhas lidas. Faça capturas de tela das mensagens originais, de preferência com timestamps, incluindo habilidades usadas e pings com recarga restante. O botão Copiar já existente permite registrar o texto de diagnóstico.
2. No checkout de desenvolvimento, o coletor existente agora respeita o locale salvo e aceita seleção explícita e duração:

   ```powershell
   .\.venv\Scripts\python.exe tools\diagnose.py --locale pt_BR --seconds 120
   ```

   Ele somente observa pixels. Você mesma realiza as ações na partida. O material fica em `assets/diagnostics/<data-hora>/`: imagens, `ocr.log`, `metadata.json` (locale/patch) e `samples.jsonl` relacionando cada leitura à imagem correspondente. `human_transcription` começa como `null`; texto de OCR não é transcrição validada. Nada é enviado automaticamente.

Compare a imagem com a leitura, preencha uma transcrição fiel e registre patch, resolução, escala do HUD, timestamp, tipo de ping e alvo. Só promova uma hipótese depois dessa comparação. Antes de compartilhar amostras, confira os nomes de jogadores e conversas visíveis. Não transforme as imagens geradas pelos testes em “capturas reais”.

## Reproduzir testes e build

Python usado para desenvolvimento: 3.11.9 x64. O executável incorpora o runtime, Qt, OpenCV, ONNX Runtime e os modelos RapidOCR. O Python instalado aqui serve apenas para desenvolver e empacotar.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
.\.venv\Scripts\python.exe tools\run_tests.py
.\.venv\Scripts\python.exe build.py
```

Saída: `dist/FlashWatch-PTBR.exe`. `--dir`, `--out` e `--console` continuam disponíveis. O empacotador inclui `LICENSE` e a licença da fonte Mulish. O arquivo MIT original deve acompanhar qualquer redistribuição.

O runner mantém o contrato original de testes como scripts independentes, grava os logs em `build/test-results` e retorna falha se qualquer suíte falhar, inclusive a de desempenho. A fixture brasileira evita rede nas novas suítes; algumas suítes originais ainda consultam Data Dragon.

Resultados e limites da localização inicial são registrados em `docs/VALIDACAO-PTBR.md`; a correção de `R` e posicionamento está em `docs/CORRECOES-R-GUIA.md`. A revisão atual de **Cartões fixos** está em `docs/ICONES-DE-RECARGA.md`: ult/Flash/outro lado a lado, ícone pronto normal e sem rótulo, ícone em recarga com cinza translúcido, X e contador embaixo. Sem recarga registrada, é considerado pronto, conforme solicitado. Os demais modos mantêm sua apresentação. As revisões anteriores permanecem documentadas em `docs/CARTOES-POR-CAMPEAO.md` e `docs/CARTOES-COMPACTOS.md`.

Os cartões permanecem depois que todas as recargas terminam, até o reset da sessão. Essa correção e sua validação estão em `docs/CARTOES-PERSISTENTES.md`. Os outros modos continuam removendo recargas prontas conforme suas configurações.
