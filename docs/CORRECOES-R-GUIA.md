# Correções de ultimate R e posicionamento do guia

26/10/2026. Revisão da entrega PT-BR anterior, preservada em `dist/FlashWatch-PTBR.exe`.

Nova build: **`dist/correcao-ult-guia/FlashWatch-PTBR.exe`**. A pasta separada permite manter o executável anterior, inclusive se estiver em uso. Feche a cópia antiga antes de abrir esta versão, quando decidir usá-la.

## Ultimate identificada como R

O parser exigia o nome da habilidade. Agora, com locale `pt_BR`, a tecla literal `R` resolve para a ultimate do campeão identificado na mensagem, com nome/ícone/cooldown vindos dos dados existentes da Riot e ID interno `ULT`.

- `Nasus R`: reconhecido como ultimate, com indicador de incerteza `?`, pois o ping sozinho não afirma que a habilidade foi usada.
- `Nasus usou R`: reconhecido como anúncio de uso. Sem segundos informados, a duração mantém a estimativa original por nível/aceleração e a marca `~`.
- A confirmação pode substituir um timer incerto; a opção de desligar o rastreamento de ultimates continua sendo respeitada.
- `Q`, `W`, `E`, texto extra e nomes ausentes não são tratados como ultimate.
- `Espere por R - 33s` e `R - Pronto(a)` não identificam campeão-alvo. O parser não usa o campeão do autor para inventar um alvo inimigo.

A captura fornecida mostra **`Nasus R`**. O formato **`<Campeão> usou R`** foi informado por você e testado como texto; não aparece nessa imagem. Os dois formatos foram testados com os 173 campeões da fixture oficial, sem cadastrar manualmente habilidades.

## Posicionar durante uma partida já aberta

O botão iniciava a demonstração, mas a atualização seguinte cancelava qualquer demonstração ao detectar uma partida. Isso fazia a barra piscar, travar e mostrar a notificação de que uma partida havia começado.

Agora:

- Fora de partida, o posicionamento continua usando exemplos.
- Em uma partida já identificada, o guia destrava a barra com os timers reais, sem inserir/remover exemplos. Mesmo vazia, a barra destravada permanece disponível para posicionamento.
- A atualização periódica não cancela esse posicionamento nem dispara a notificação incorreta.
- Concluir o guia ou mudar de sessão restaura o bloqueio e os cliques através da barra.
- A demonstração iniciada fora de partida continua terminando quando uma nova partida começa.

O texto dessa etapa foi corrigido nos três idiomas. É a única alteração intencional nos pares FR/EN originais desta revisão; as outras 345 entradas originais permanecem iguais.

## Testes realizados sem usar o jogo aberto

Seu pedido de **não testar nem capturar a partida aberta** foi respeitado. A nova build não foi executada. A verificação do executável foi estática, incluindo inspeção do código empacotado das duas correções.

Os testes do guia usam estado de partida simulado e objetos substitutos. O teste de integração da aplicação também recebeu bloqueios explícitos: detector simulado sem jogo e qualquer tentativa de captura real gera falha. Nenhum comando, tecla ou clique foi enviado ao LoL.

Resultado: **32 suítes aprovadas de 33 executadas**. A suíte restante é a de desempenho, com **8/9 verificações aprovadas**. O limite não foi alterado: a leitura de um chat modificado levou 1.021 ms contra o máximo de 900 ms, tanto na execução conjunta quanto na repetição separada. Essa medição é de OCR, antes do parser, e o algoritmo OCR não foi modificado nesta revisão. O motivo da variação de tempo não foi atribuído a um processo específico.

Passaram, entre outros:

- 13 métodos PT-BR de parser/locale, incluindo 346 combinações de campeão e formato `R`/`usou R`, falsos positivos, confirmação e opção de rastreamento.
- 4 testes de posicionamento: partida já aberta, preservação de timers reais, conclusão do guia e troca de sessão; o caminho de início de uma nova partida também foi conferido.
- 3 testes de OCR, incluindo a imagem brasileira fornecida e as regressões anteriores.
- 100 verificações da integração da aplicação com captura real proibida.
- Compatibilidade com inglês/francês, renderização da UI, layouts, configurações e atualização.

Logs: `build/correcao-r-guia-tests/`. A primeira reprodução do defeito fica em `build/ultimate-r-before.log` e `build/guide-placement-before.log`. Verificação estática do pacote: `build/package-r-guia-verification.json`.

## O que a captura brasileira validou — e seus limites

O arquivo original foi preservado em `tests/fixtures/pt_BR/client-ultimate.png`, sem edição. O manifesto ao lado registra hash, dimensões e transcrição. O teste lê apenas esse arquivo salvo.

No recorte manual de chat, o OCR reconheceu os pings `Nasus R` de **07:09** e **07:14**, ambos convertidos corretamente para `Nasus / ULT`, com nomes oficiais e incerteza. A mensagem `Espere por R - 33s` foi lida e descartada corretamente por não nomear alvo. Nenhum evento foi atribuído ao Kayn que enviou os pings.

**Cobertura parcial:** os pings `Nasus R` de 01:02 e 07:44 não foram lidos nesse passe. Além disso, a localização automática escolheu uma área errada nessa imagem; a validação bem-sucedida usa o recorte manual, equivalente ao recurso Enquadrar chat já existente. Esta correção não altera o detector nem certifica que ele encontre o chat automaticamente nessa cena. Não houve nova captura nem teste em partida real.

A amostra inglesa embutida passa a reconhecer também a linha real `Lillia R` quando executada com dados brasileiros, além dos dois feitiços anteriormente esperados. Os testes conferem os nomes de ultimates e feitiços separadamente.

## Arquivos desta revisão

| Arquivo | Alteração |
| --- | --- |
| `src/message_parser.py` | Resolução estrita de `R` para a ultimate do alvo |
| `src/main.py` | Posicionamento ao vivo sem demonstração; restauração do bloqueio |
| `src/i18n.py` | Instrução de posicionamento atualizada em PT/EN/FR |
| `tests/test_ptbr.py` | Casos `R`, confirmação, opções e falsos positivos |
| `tests/test_ptbr_ocr.py` | Leitura da captura fornecida e nomes de ultimate no self-test |
| `tests/test_guide_placement.py` | Regressões do guia com estado simulado |
| `tests/test_app_shell.py` | Proibição explícita de captura/jogo real no teste de integração |
| `tests/fixtures/pt_BR/client-ultimate.png` | Captura fornecida, preservada |
| `tests/fixtures/pt_BR/client-ultimate.json` | Proveniência e transcrição |
| `docs/PTBR.md` | Evidências e limitações atualizadas |
| `docs/CORRECOES-R-GUIA.md` | Este relatório |

Os timers, fontes ampliadas, layouts, captura, algoritmo OCR e tabela de cooldowns mantêm o comportamento da entrega anterior. A captura brasileira dos testes **não foi incluída no executável**. Licenças MIT e Mulish continuam incorporadas.

## Build

Comando: `.\.venv\Scripts\python.exe build.py --out dist/correcao-ult-guia`.

- Arquivo: `FlashWatch-PTBR.exe`.
- Tamanho: 107.698.686 bytes (aproximadamente 102,7 MiB).
- SHA-256: `ec740c9bf39647d3a4b81d917f16f0889e958c0e8939903ef80d3097f7df2621`.
- Runtime Python, Qt, três modelos OCR e licenças presentes no pacote.
- Métodos de resolução de `R` e posicionamento corrigido confirmados no código empacotado, sem executar a aplicação.
- Sem publicação de release ou alteração da instalação em uso.
