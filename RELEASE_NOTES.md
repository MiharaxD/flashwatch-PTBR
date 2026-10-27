# FlashWatch PT-BR v1.0.0-ptbr

Primeira release desta edição brasileira, baseada no Flashwatch original e preservando a licença MIT.

## Downloads

- **FlashWatch-PTBR-Setup.msi**: instalador por usuário, com atalho no menu Iniciar, opção de atalho na área de trabalho e desinstalação pelo Windows.
- **FlashWatch-PTBR.exe**: versão portátil do mesmo aplicativo.
- **SHA256SUMS.txt**: hashes para conferir os arquivos.

Não é necessário instalar Python. Feche a versão antiga pela bandeja antes de instalar ou abrir a nova. O instalador não inicia o aplicativo ao concluir e preserva as configurações e o cache na desinstalação.

## O que mudou

- Interface em Português Brasileiro, mantendo inglês e francês.
- Nomes oficiais brasileiros de campeões, feitiços e ultimates pelo Data Dragon, com os identificadores e o cache preservados.
- Reconhecimento PT-BR, incluindo `Campeão R` e `Campeão usou R`, mantendo as marcações de incerteza e de duração aproximada.
- Cartões fixos agrupados por campeão: retrato acima de ult / Flash / outro feitiço. Pronto aparece com ícone normal; recarga recebe cinza translúcido, X e contador embaixo.
- Cartões permanecem quando tudo fica pronto, até o reset da sessão. Linha do tempo e Linhas compactas preservam seu comportamento.
- Correções de legibilidade dos números, posicionamento pelo guia e encerramento do programa.
- Instalador nativo do Windows com licenças e documentação.

## Validação e limites

- Aplicativo: **35/35 suítes passaram**, incluindo permanência dos cartões por uma hora simulada após o fim das recargas, novo uso, reset e compatibilidade dos outros modos.
- Instalador: **42/42 verificações passaram**, incluindo integridade e extração dos 13 arquivos, hashes, tabelas de atalhos/desinstalação e planejamento pelas APIs nativas do Windows.
- Instalação, reparação e desinstalação completas **não foram executadas**. A tentativa de extração administrativa com `msiexec /a` atingiu o limite de tempo; extração por 7-Zip e planejamento nativo passaram.
- Nenhuma partida aberta foi capturada ou controlada nesta validação. A fixture brasileira fornecida anteriormente foi reconhecida parcialmente; localização automática da área de chat e demais formatos ainda têm limitações documentadas. Frases sem evidência continuam identificadas como hipóteses.
- Cooldowns base não foram certificados como atuais; ultimates sem contagem explícita continuam aproximadas.
- Pacote local sem assinatura Authenticode. Os binários já validados foram preservados: a versão interna do aplicativo continua `0.0.0-dev`, e o MSI identifica seu pacote como `1.0.0`.
- O atualizador interno ainda aponta para o projeto original e exige o nome PT-BR do arquivo; use os downloads desta release para esta edição.

Relatórios completos em [docs](https://github.com/MiharaxD/flashwatch-PTBR/tree/main/docs). Os arquivos de licença e avisos também acompanham a release e o instalador.

## SHA-256

```text
cf12ec2728af58ad7633b476e5699d6586cc3e99892aa5e2da50eaa8e3ffe5a7  FlashWatch-PTBR-Setup.msi
2a68302e15d94143d3127e98dad18d8e34916e0364146bbdb7b8079ad1cb7d4a  FlashWatch-PTBR.exe
```

Projeto original: [abenfraj/flashwatch](https://github.com/abenfraj/flashwatch). Esta edição é uma modificação local e não é uma release oficial do projeto original nem um produto endossado pela Riot Games.
