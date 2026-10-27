# Cartões fixos: ícones lado a lado — 26/10/2026

Correção da disposição solicitada pelo usuário, exclusivamente no modo **Cartões fixos**:

```text
        Retrato do campeão
     Ult     Flash     Outro
    ~1:43    1:45        ✓
```

Cada campeão aparece uma vez. A ultimate fica à esquerda, a posição do Flash é reservada no meio e o outro feitiço fica à direita. O tempo fica centralizado embaixo de seu ícone. A ordem não representa as teclas D/F do adversário.

**✓ verde substitui PRONTO**, tanto para uma contagem encerrada quanto para espaços sem recarga registrada, como solicitado. O símbolo é desenhado com traços, sem depender de um caractere disponível na fonte. Sem dados observados, essa indicação continua sendo uma suposição de apresentação; não gera timers nem altera reconhecimento, notificações ou cálculo de cooldown.

O espaço reservado ao Flash usa o ícone oficial já disponível, mesmo sem uma recarga registrada. A identidade do outro feitiço permanece genérica até ser reconhecida. Quando há recargas extras por troca de feitiço, elas continuam disponíveis em uma segunda fileira do mesmo cartão, com o número embaixo do ícone.

A altura padrão caiu de 164 para 128 pixels. A largura depende das contagens presentes, incluindo espaço para as marcações originais `~` e `?`; o texto PRONTO deixa de ocupar espaço. A posição e o tamanho salvos continuam respeitados, com tamanho mínimo suficiente para um cartão completo. Uma moldura estreita demais pode exigir redimensionamento para comportar todos os campeões, como antes.

Linha do tempo e Linhas compactas preservam seu desenho e o texto de pronto. Captura, OCR, parser, Data Dragon, timers, configurações de segurança e regras de visibilidade não foram alterados nesta revisão. As correções anteriores permanecem incluídas.

## Arquivos alterados nesta revisão

| Arquivo | Alteração |
| --- | --- |
| `src/overlay.py` | Colunas ult/Flash/outro, tempo abaixo dos ícones, ✓ vetorial e medidas compactas |
| `src/onboarding.py` | Prévia dos cartões e altura da moldura no guia |
| `src/ui.py` | Miniatura de Cartões fixos |
| `src/i18n.py` | Descrição do layout nos três idiomas |
| `src/settings.py` | Comentário da opção, sem mudar seu valor padrão |
| `tests/test_champion_cards.py` | Alinhamento, reserva do Flash, ✓, estado preservado, idiomas, escalas, temas e outros modos |
| `README.md`, `NOTICE-PTBR.md`, `docs/PTBR.md` | Referência à revisão |
| `docs/CARTOES-COMPACTOS.md` | Este relatório |

## Verificação

As prévias em `build/champion-cards-compact/` foram geradas pelo renderizador real usando Qt fora da tela e dados simulados, incluindo cinco campeões em áreas equivalentes a 1080p e 1440p, nos três temas. Os sete testes específicos verificam também que textos e ícones não se sobrepõem, que o tempo fica abaixo do ícone, que recargas adicionais não são descartadas dentro do cartão e que o símbolo não modifica o timer original.

Nenhuma captura de partida aberta, comando no jogo ou execução da nova build foi realizado. As limitações de OCR descritas em `CORRECOES-R-GUIA.md` permanecem; não houve nova validação sobre uma partida nem em um monitor 1440p físico.

**34/34 suítes passaram**, incluindo os sete testes específicos dos cartões. A suíte de desempenho passou em 9/9 verificações, mantendo o limite original: leitura alterada de 16 linhas em 895 ms (limite 900 ms). Tempos variam com a máquina e sua carga.

Comando: `.venv/Scripts/python.exe tools/run_tests.py --out build/champion-cards-compact-tests`. Resultados: `build/champion-cards-compact-tests/results.json`; logs completos na mesma pasta. `git diff --check` também passou.

## Build

Nova saída: `dist/cartoes-compactos/FlashWatch-PTBR.exe`. As versões anteriores foram preservadas. O executável inclui o runtime Python, Qt, modelos OCR e licenças; não precisa de Python instalado na máquina de destino. A licença MIT original e a licença da fonte Mulish acompanham o pacote.

**47/47 verificações estáticas passaram**. Os módulos alterados correspondem às fontes finais; os métodos de desenho da barra/lista e os outros 20 módulos da aplicação mantêm o mesmo código compilado da build anterior. A inspeção confirmou runtime Python, plugin Qt do Windows, três modelos OCR, licenças e ausência das capturas fornecidas pelo usuário no executável.

Relatório: `build/package-champion-cards-compact-verification.json`. A build foi inspecionada como arquivo, sem abri-la, respeitando o pedido de não testar com o LoL aberto. Essa inspeção não equivale a um teste de abertura do executável.

Build de 107.703.179 bytes. SHA-256:

```text
ee4e1dfa45ac806fc178e012667b41ea24ca904e485e283ca6ea69ec149ba579
```

Comando: `.venv/Scripts/python.exe build.py --out dist/cartoes-compactos`.
