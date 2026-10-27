# Cartões fixos: estado no ícone — 26/10/2026

Revisão visual solicitada, exclusivamente em **Cartões fixos**, mantendo o retrato do campeão acima de ult / Flash / outro feitiço.

- **Pronto:** ícone normal, sem texto, contador ou ✓ embaixo.
- **Em recarga:** camada cinza com aproximadamente 32% de opacidade sobre o ícone, um X central e o contador original embaixo. As cores da imagem continuam visíveis por baixo.
- Quando a contagem acaba, o ícone volta ao normal e o contador desaparece.
- Sem recarga registrada, o ícone é considerado pronto, conforme solicitado anteriormente. Essa suposição visual não cria timers nem confirma uso.

A camada fica recortada ao círculo do ícone. O retrato do campeão não recebe cinza nem X, e o contador preserva cores e marcações `~` / `?`. As imagens em cache não são modificadas; a camada é desenhada por cima, sem filtros de imagem executados a cada atualização.

As posições e medidas dos cartões permanecem as da revisão compacta. Feitiços adicionais por troca continuam sendo apresentados. Linha do tempo e Linhas compactas preservam seu comportamento e texto de pronto.

## Arquivos desta revisão

| Arquivo | Alteração |
| --- | --- |
| `src/overlay.py` | Remove o ✓ dos cartões; desenha cinza translúcido e X somente em habilidades com contagem ativa |
| `src/onboarding.py` | Prévia do guia usa a mesma camada de recarga e deixa o espaço abaixo dos ícones prontos vazio |
| `src/ui.py` | Miniatura de Cartões fixos atualizada |
| `src/i18n.py` | Descrição do comportamento em português, inglês e francês |
| `src/settings.py` | Comentário da opção atualizado, sem mudar configurações |
| `tests/test_champion_cards.py` | Oito testes específicos, incluindo transparência real, X visível, recorte e preservação dos outros modos |
| `README.md`, `NOTICE-PTBR.md`, `docs/PTBR.md` | Referências à revisão atual |
| `docs/ICONES-DE-RECARGA.md` | Este relatório |

Não houve alteração de captura, OCR, parser, Data Dragon, cálculo dos cooldowns, notificações, persistência de timers ou comportamento de segurança nesta revisão. As correções anteriores permanecem na build.

## Validação e limites

Os testes específicos usam Qt fora da tela e dados locais. Um teste de pixels verifica que a máscara é translúcida, que o X é visível e que pixels fora do ícone não são afetados. Outros verificam que ícones prontos não recebem camada nem rótulo, nos três idiomas, e que barra/lista continuam exibindo o texto de pronto original. Prévia, guia, escalas e três temas também são conferidos.

Artefatos em `build/champion-cards-icons/`, incluindo cinco campeões em áreas equivalentes a 1080p e 1440p. São imagens do renderizador com dados simulados, não capturas de partida.

**34/34 suítes passaram**, incluindo os oito testes específicos dos cartões. Desempenho: 9/9 verificações; leitura alterada de 16 linhas em 845 ms, dentro do limite original de 900 ms. Os limites não foram flexibilizados; tempos variam conforme a máquina e sua carga.

Comando: `.venv/Scripts/python.exe tools/run_tests.py --out build/champion-cards-icons-tests`. Logs completos nessa pasta; resumo em `build/champion-cards-icons-tests/results.json`. `git diff --check` passou.

Nenhuma partida aberta foi capturada, controlada ou usada para testes; a nova build não foi executada. A validação sobre o jogo e em monitor 1440p físico permanece pendente. As limitações de OCR de `CORRECOES-R-GUIA.md` continuam válidas.

## Build

Saída: `dist/icones-de-recarga/FlashWatch-PTBR.exe`. As builds anteriores foram preservadas. O pacote incorpora runtime Python, Qt, modelos OCR e licenças; não requer instalação de Python na máquina de destino. Licença MIT original e licença Mulish preservadas.

**48/48 verificações estáticas passaram**. Os módulos alterados correspondem às fontes finais. Os métodos da barra/lista e os outros 20 módulos da aplicação mantêm o código compilado da build compacta anterior. Confirmados: máscara usada somente nos cartões, ausência de rótulo para pronto, runtime Python, plugin Qt do Windows, três modelos OCR, licenças e ausência de capturas fornecidas pelo usuário no executável.

Relatório: `build/package-champion-cards-icons-verification.json`. A inspeção não abriu o executável e não substitui um teste de execução.

Build de 107.703.599 bytes. SHA-256:

```text
30a8ffb10d43540ceb47675ad3e7bce904c6deaf19715e74aa582b624a0424d5
```

Comando: `.venv/Scripts/python.exe build.py --out dist/icones-de-recarga`.
