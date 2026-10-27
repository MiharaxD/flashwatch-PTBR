# Validação da entrega PT-BR

Data: 26/10/2026. Base original: `5193229865fbd4de266d9d9aff4ada6d8b2e2f77`.

## Resultado

**32/32 suítes aprovadas**, incluindo as **28 suítes originais** e **4 suítes PT-BR novas**. A suíte de desempenho também foi executada, sem exclusão. Logs finais completos em `build/final-validation/`; resumo por suíte em `build/final-validation/results.json`.

Antes das modificações, as 28 suítes originais passaram em uma cópia separada do commit original (`build/baseline-tree`), com logs em `build/baseline/`. Nenhuma aprovação foi inferida a partir da simples compilação.

| Verificação | Resultado |
| --- | --- |
| Catálogo | 366 chaves com três traduções; placeholders e marcação conferidos |
| Preservação FR/EN | Os 346 pares originais mantidos exatamente, comparados com a base |
| Loader Data Dragon | `pt_BR`, cache por versão/locale e IDs preservados; fixture oficial `16.21.1` |
| Parser | Os 11 feitiços e 173 nomes de ultimates da fixture reconhecidos em frases sintéticas derivadas do formato documentado |
| Idiomas existentes | Suítes originais em inglês/francês e casos de compatibilidade aprovados |
| Falsos positivos | Negações, conversa comum, verbo dentro de outra palavra, habilidade de outro campeão, contagens inválidas e hipóteses com texto extra descartados |
| Hipóteses de cooldown PT-BR | Mantêm indicador de incerteza e não são promovidas a formatos reais do cliente |
| OCR PT-BR | Frames sintéticos em 1080p, 1440p e 4K aprovados; chat apagado sem sobreposição também aprovado |
| OCR com oclusão | Em uma imagem sintética com chat apagado sobre cenário carregado, 3 dos 4 eventos ficaram legíveis; nenhum evento incorreto foi emitido. O contrato exige descarte seguro, não reconhecimento de texto coberto |
| Captura real incluída | Amostra original em **inglês**, confirmada pelo manifesto `resources/test/chat-sample.json`; 2/2 eventos reconhecidos com nomes exibidos em português |
| UI | Quatro páginas da janela de controle e oito telas do guia renderizadas; seleção e persistência dos três idiomas aprovadas |
| Funções | Rótulos brasileiros na UI, IDs como `JUNGLE`/`SUPPORT` mantidos nos callbacks e no estado |
| Números da barra | Regressão reproduzida antes: 0 contagens com fonte de 6 px; corrigida depois: todos os números desenhados. `test_bar_layout.py`: 45/45 verificações |
| Legibilidade | Padrão alterado de 0,5× para 1,5× após seu pedido; fonte com pelo menos 16 px no teste de renderização, dentro da barra em áreas equivalentes a 1080p/1440p |
| Tamanhos e layouts | Testes de posicionamento, colisões, cartões, linhas e fontes aprovados; valores de tamanho já salvos preservados |
| Cooldowns e licença | Tabela base de cooldowns e arquivo MIT idênticos à base original |
| Compilação | Executável Windows único, com Python 3.11, Qt, três modelos OCR e licenças no pacote |

As quatro suítes novas contêm 19 métodos de teste, além dos casos parametrizados e subtestes. Isso não significa 19 capturas de partidas.

## Desempenho observado

A suíte original de desempenho passou nas 9 verificações. No ambiente desta execução, o custo ocioso medido foi aproximadamente 0,306 ms por frame, equivalente a 0,15% de um núcleo a 5 Hz; uma leitura com chat alterado levou aproximadamente 760 ms. São medições desta máquina, não garantias universais de FPS/CPU em uma partida real.

Os algoritmos de captura, segmentação, cache de linhas e reconhecimento não foram alterados. Em `src/ocr.py`, apenas a mensagem inicial passou pelo catálogo.

## Smoke do executável

O arquivo foi copiado sozinho para `build/smoke-install` e iniciado com `PATH` contendo somente os diretórios do Windows, sem `PYTHONHOME` ou `PYTHONPATH`. A build carregou o próprio runtime e os modelos OCR.

Foram conferidos:

1. Primeiro uso, download dos dados/357 ícones e oito telas do guia.
2. Troca para `pt_BR`, carregamento de 173 campeões e 11 feitiços, persistência do idioma.
3. Teste embutido dentro do executável: 9 linhas reconhecidas como chat e os 2 eventos esperados, com Yasuo/Exaustão e Karma/Curar.
4. Nova inicialização com os proxies HTTP(S) apontando para uma porta local fechada: falha de rede registrada, recuperação do patch pelo cache e OCR funcionando.
5. Contagem visível e decrescente sob os ícones, incluindo o tamanho ampliado de 1,5×.
6. Encerramento pela interface: nenhuma cópia de teste permaneceu em execução e o token de instância única foi liberado.

Evidências locais: `build/smoke-install/assets/flashwatch.log`, `build/smoke-install/launch.json`, `build/smoke-install/exit-check.json`, `build/package-verification.json` e `build/ptbr-ui/`.

A primeira tentativa de empacotamento incluiu uma ICU de outra ferramenta do ambiente e falhou ao importar QtCore. O build agora restringe a busca de DLLs aos diretórios do Python ativo e do Windows, mantendo os hooks dos pacotes. A build entregue passou nas verificações acima. O smoke também revelou que um pedido Qt de saída podia ser vetado pelo comportamento de ocultar a janela; a saída explícita após salvar corrigiu o processo remanescente.

## Executável entregue

- Arquivo: `dist/FlashWatch-PTBR.exe`.
- Tamanho: 107.697.350 bytes (aproximadamente 102,7 MiB).
- SHA-256: `98c8232c6bd4c4f1573caedf223539e0442ba2d7ea1471af9e185b288fbc2fb2`.
- Python de build: 3.11.9 x64.
- PyInstaller 6.22.3; PySide6 6.12.0; RapidOCR ONNX Runtime 1.4.4; ONNX Runtime 1.31.1; OpenCV 5.0.0.93; NumPy 2.4.6.
- Dependências completas registradas em `build/build-environment.txt`, também copiadas para a pasta de distribuição.
- Sem publicação de release e sem assinatura digital. O atualizador exige um asset com o nome PT-BR para preservar a localização.

## Arquivos alterados/adicionados

| Arquivo | Modificação |
| --- | --- |
| `src/i18n.py` | Catálogo PT-BR completo, terceiro idioma, mensagens auxiliares |
| `src/ui.py` | Seletor de três idiomas, funções com IDs preservados e tamanho inicial consistente |
| `src/onboarding.py` | Cartão/bandeira brasileiros, três idiomas e tamanho inicial consistente |
| `src/message_parser.py` | `usou`, variação sintética `us0u`, hipóteses delimitadas de cooldown e artigos em nomes oficiais |
| `src/riot_assets.py` | Fallback de nome genérico pelo catálogo; loader/cache mantidos |
| `src/cooldowns.py` | Aliases brasileiros, sem alterar os valores base |
| `src/roles.py` | Aliases brasileiros, funções canônicas mantidas |
| `src/timer_manager.py` | PRONTO e preservação da incerteza das hipóteses |
| `src/overlay.py` | Medição de PRONTO e correção da contagem invisível com fontes pequenas |
| `src/settings.py` | Locale documentado e padrão de contagem em 1,5× |
| `src/ocr.py` | Mensagem inicial localizada |
| `src/self_test.py` | Erro de imagem localizado |
| `src/updater.py` | Mensagens localizadas e exigência do asset PT-BR |
| `src/main.py` | Encerramento explícito do loop Qt após salvar |
| `build.py` | Nome do executável, licenças e isolamento da busca de DLLs |
| `.github/workflows/release.yml` | Nome PT-BR nos caminhos do artifact |
| `tests/test_language.py` | Validação do catálogo com três idiomas |
| `tests/test_bar_layout.py` | Regressão dos números ocultos e limites de desenho |
| `tests/test_display_choice.py` | Área suficiente para quatro cartões com a fonte ampliada |
| `tests/test_sound_and_type.py` | Novo padrão de tamanho solicitado |
| `tests/test_ptbr.py` | Parser, locale, dados oficiais, aliases e falsos positivos |
| `tests/test_ptbr_ui.py` | UI, persistência e legibilidade 1080p/1440p |
| `tests/test_ptbr_ocr.py` | OCR sintético brasileiro e captura inglesa com dados brasileiros |
| `tests/test_ptbr_packaging.py` | Nome, licenças, ambiente de build e proteção do atualizador |
| `tests/ptbr_assets.py` | Loader offline para os testes brasileiros |
| `tests/fixtures/pt_BR/ddragon.json` | Campos de dados oficiais da Riot com proveniência |
| `tools/diagnose.py` | Locale, duração e amostras locais vinculadas às capturas |
| `tools/run_tests.py` | Execução dos scripts de teste com logs e resultado agregado |
| `README.md` | Identificação da localização e caminhos da build |
| `NOTICE-PTBR.md` | Créditos e avisos preservados |
| `docs/PTBR.md` | Arquitetura, evidências, uso, coleta e reprodução |
| `docs/VALIDACAO-PTBR.md` | Este relatório |

`LICENSE`, as artes, a captura original, o detector de chat, o detector do jogo, o leitor de funções e os arquivos de áudio não foram modificados. Artefatos gerados ficam em `build/` e `dist/`, ignorados pelo Git.

## Limitações ainda pendentes

- **Não há captura real do cliente brasileiro disponível neste checkout.** O verbo tem evidência textual oficial da Riot; o reconhecimento em pixels brasileiros ainda precisa de validação numa partida.
- `Aguarde`/`Espere` com segundos são hipóteses, não frases afirmadas como reais. O coletor está preparado, mas não foi executado contra uma partida brasileira nesta sessão.
- O teste real distribuído usa inglês. Os frames brasileiros dos testes são artificiais e estão identificados como sintéticos.
- Cooldowns, modificadores e exceções especiais mantêm o comportamento original; não foram certificados como atuais para todos os campeões/modos. Nenhum ajuste de balanceamento foi inventado.
- A sessão usou monitor 1920×1080. 1440p/4K foram simulados nos testes de renderização/OCR; legibilidade física num monitor 1440p ainda não foi avaliada.
- A máquina de teste possui Python para desenvolvimento. A ausência de dependência externa foi verificada pelo pacote e pelo `PATH` isolado; não houve instalação em uma VM Windows limpa sem Python.
