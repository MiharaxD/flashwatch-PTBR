# Anúncio de Flash Hextec confirma o Flash normal — 27/10/2026

O usuário relatou que, quando um adversário tem Flashtração Hextec e usa Flash, o ping pode anunciar **`<Campeão> usou Flash Hextec`**. O pedido é tratar essa linha como uso confirmado do **Flash normal**, preservando nome, ícone e cooldown existentes.

O parser PT-BR agora normaliza esse nome somente no caminho de anúncio de uso. O evento resultante mantém `kind="summoner"`, chave canônica `Flash`, nome oficial `Flash`, ícone `SummonerFlash` e `certain=True`. A linha original continua nos diagnósticos.

- O contador usa o mesmo cooldown do Flash comum e os mesmos modificadores já existentes. Não cria um feitiço nem um timer separado para o Flash Hextec de 20 segundos.
- A confirmação de uma entrada incerta usa o comportamento já existente do gerenciador.
- Anúncios `Flash` e `Flash Hextec` do mesmo campeão e horário compartilham a assinatura de deduplicação.
- O nome só é normalizado em anúncios com verbo de uso. Não converte um ping simples ou uma mensagem de espera de 20 segundos em cooldown do Flash normal.
- A extensão exige um campeão resolvido de forma estrita para evitar frases como `Alistar não usou Flash Hextec`. Mantém a exigência de capitalização nas linhas atribuídas a um autor.
- Inglês e francês não recebem esse alias brasileiro. Chamadas livres de jogadores preservam sua interpretação anterior como eventos incertos.
- `F1ash Hextec` e a ausência do espaço entre as palavras são tolerâncias artificiais de OCR usadas nos testes, não exemplos documentados do cliente.

## Evidência

O formato completo do anúncio veio do relato do usuário em 27/10/2026. **Não foi fornecida captura dessa nova linha.** A correção não equivale a validação visual no cliente.

O Data Dragon oficial, patch `16.21.1` retornado na consulta, apresenta a runa `HextechFlashtraption` como **Flashtração Hextec** e sua descrição nomeia **Flash Hextec** como substituto enquanto Flash está em recarga, com cooldown próprio de 20 segundos. Isso confirma o nome e a mecânica, mas não comprova o formato exato do chat. O anúncio relatado é mapeado para o Flash comum por solicitação explícita do usuário.

Fontes: [runa brasileira na Riot](https://ddragon.leagueoflegends.com/cdn/16.21.1/data/pt_BR/runesReforged.json) e [feitiços brasileiros na Riot](https://ddragon.leagueoflegends.com/cdn/16.21.1/data/pt_BR/summoner.json). Esses dados não motivaram alteração nos valores de cooldown do aplicativo.

## Arquivos e verificação

- `src/message_parser.py`: normalização restrita do anúncio PT-BR.
- `tests/test_hextec_flash.py`: oito testes, incluindo todos os campeões da fixture, confirmação, ícone, duração, deduplicação, falsos positivos e preservação de inglês/francês.
- `docs/FLASH-HEXTEC.md`: este registro e os limites de evidência.
- `build_installer.py` e `docs/INSTALADOR.md`: binário fixado e metadados do MSI local 1.0.1, preservando o instalador anterior.
- `tools/verify_installer.py`: valida o caminho do novo pacote e executa o planejamento nativo novamente, sem reutilizar o resultado anterior.

Não houve alteração no desenho da interface, captura, OCR, gerenciador de timers ou comportamento de segurança. Nenhuma partida aberta foi usada ou capturada. O arquivo local não relacionado `design/maquette/flashwatch-lol-client-demo.html` foi preservado.

**36/36 suítes passaram**, incluindo os oito testes novos de Flash Hextec. Desempenho: 9/9 verificações; leitura alterada de 16 linhas em 762 ms, dentro do limite original de 900 ms. Os limites não foram flexibilizados. Logs: `build/hextec-flash-tests/`, resumo em `results.json`.

As versões anteriores e a release publicada continuam preservadas; esta revisão não é publicada automaticamente. O aplicativo atualizado fica em `dist/flash-hextec/FlashWatch-PTBR.exe`, e o instalador atualizado fica em `dist/flash-hextec/instalador/FlashWatch-PTBR-Setup.msi`.

O executável tem 107.705.202 bytes, SHA-256 `b9d73c96ee072ac7a82a4f41d3f80d30d00345813d4e8fd75173023e1fdef3c5`. **55/55 verificações estáticas passaram**: o parser corresponde à fonte final e os outros 23 módulos da aplicação, incluindo o renderizador, cálculo de cooldowns e captura, mantêm o mesmo código compilado. A build foi inspecionada como arquivo, sem executá-la.
