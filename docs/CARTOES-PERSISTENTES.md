# Cartões fixos permanecem quando tudo está pronto — 26/10/2026

Correção solicitada: o campeão não deve desaparecer de **Cartões fixos** quando todas as habilidades voltam a ficar prontas.

O programa já removia timers encerrados após o prazo de exibição de pronto. Como os cartões usavam somente essa lista, o último timer removido fazia o campeão inteiro sumir. Agora os registros encerrados são guardados separadamente para a apresentação dos cartões, mantendo o retrato e os ícones conhecidos em seu estado normal, sem contador nem X.

- Somente Cartões fixos pede a lista com os registros prontos. Linha do tempo e Linhas compactas mantêm o comportamento anterior, incluindo o prazo para sumir e a opção de ocultar prontos.
- O registro guardado não é uma recarga ativa: não entra na contagem de habilidades em recarga, não bloqueia um novo uso e não repete sons ou avisos.
- Um novo uso da mesma habilidade substitui o registro anterior na apresentação, sem criar duas entradas do mesmo feitiço.
- O reset já existente limpa também os cartões guardados: zerar timers, fim/troca de partida, reinício de relógio confirmado e troca de idioma.
- Encerrar a demonstração remove também os cartões de demonstração que já estavam prontos, preservando os registros fora dela conforme as regras existentes.
- A memória é temporária e limitada pelas combinações de campeão/habilidade reconhecidas na sessão. Não é gravada nas configurações e não é restaurada após fechar o aplicativo.

Nos cartões, as habilidades prontas permanecem mesmo após o prazo de desaparecimento ou com a opção de ocultar prontos ligada. Os outros modos continuam obedecendo a essas configurações. O desenho anterior foi preservado: retrato acima de ult / Flash / outro, pronto normal e sem texto, recarga com cinza translúcido, X e contador embaixo.

## Arquivos alterados

| Arquivo | Alteração |
| --- | --- |
| `src/timer_manager.py` | Guarda registros purgados para apresentação; `snapshot(keep_ready=True)` os inclui; resets e fim da demonstração limpam os registros correspondentes |
| `src/main.py` | Solicita a apresentação persistente somente em Cartões fixos, também na demonstração |
| `tests/test_persistent_cards.py` | Sete testes de expiração real, permanência, novo uso, reset, demonstração, funções e reinício de relógio |
| `tests/test_guide_placement.py` | Integração da atualização da interface: cartões persistem, barra/lista não, reset e fim de sessão limpam |
| `README.md`, `NOTICE-PTBR.md`, `docs/PTBR.md` | Referências à revisão |
| `docs/CARTOES-PERSISTENTES.md` | Este relatório |

Não houve mudança no reconhecimento, captura, Data Dragon, duração dos cooldowns, deduplicação, alertas, janelas ou comportamento de segurança. A lista original de timers ativos continua sendo purgada normalmente.

## Validação

Os testes específicos avançam um relógio simulado: após o encerramento e a remoção dos timers ativos, avançam mais uma hora e verificam o cartão com os três ícones, sem contadores, máscara de recarga ou novos alertas. Também verificam um novo uso, a correção de função e as diferentes limpezas de sessão. A integração da interface usa estado de partida simulado.

Prévia: `build/persistent-cards/all-ready-after-one-hour.png`. Nenhuma partida aberta foi capturada ou controlada; o executável desta revisão não foi aberto. A validação sobre o jogo continua pendente, conforme a restrição do usuário. Permanecem as limitações de OCR descritas em `CORRECOES-R-GUIA.md`.

**35/35 suítes passaram**, incluindo sete testes novos de persistência e duas verificações adicionais da integração da interface. A suíte de desempenho passou em 9/9 verificações: leitura alterada de 16 linhas em 861 ms, dentro do limite original de 900 ms. Tempos dependem da máquina e de sua carga.

Comando: `.venv/Scripts/python.exe tools/run_tests.py --out build/persistent-cards-tests`. Resultados: `build/persistent-cards-tests/results.json`; logs completos na mesma pasta. `git diff --check` passou.

## Build

Saída: `dist/cartoes-persistentes/FlashWatch-PTBR.exe`. As builds anteriores foram preservadas. Runtime Python, Qt, modelos OCR e licenças estão incorporados. O destino não precisa de Python instalado. Licença MIT original e licença Mulish preservadas.

**130/130 verificações estáticas passaram**, incluindo correspondência dos dois módulos alterados com as fontes finais, 22 módulos sem alteração (inclusive todo o renderizador, captura e OCR), métodos inalterados de cálculo, deduplicação e alertas, runtime Python, plugin Qt do Windows, três modelos OCR e licenças.

Relatório: `build/package-persistent-cards-verification.json`. A comparação foi feita com a build anterior de ícones de recarga, sem executar o aplicativo. A inspeção estática não substitui um teste de abertura.

Build de 107.703.384 bytes. SHA-256:

```text
2a68302e15d94143d3127e98dad18d8e34916e0364146bbdb7b8079ad1cb7d4a
```

Comando: `.venv/Scripts/python.exe build.py --out dist/cartoes-persistentes`.
