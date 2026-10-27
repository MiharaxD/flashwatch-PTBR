# FlashWatch PT-BR v1.0.2-ptbr

Atualização da edição brasileira, baseada no Flashwatch original e preservando a licença MIT. Aplicativo e instalador identificam esta build como **1.0.2**.

## Downloads

- **FlashWatch-PTBR-Setup.msi**: instalador por usuário, com atalho no menu Iniciar, opção de atalho na área de trabalho e desinstalação pelo Windows.
- **FlashWatch-PTBR.exe**: versão portátil do mesmo aplicativo.
- **SHA256SUMS.txt**: hashes para conferir os arquivos.

Não é necessário instalar Python. Feche a versão antiga pela bandeja antes de instalar ou abrir a nova. O instalador não inicia o aplicativo ao concluir e preserva as configurações e o cache na desinstalação.

**Instale esta versão uma vez para ativar o atualizador brasileiro.** As cópias antigas ainda apontam para o projeto original. Os anexos com sufixo `-v1.0.0` são históricos; para a versão atual, escolha os nomes sem esse sufixo.

## O que mudou

- Verificação do GitHub **MiharaxD/flashwatch-PTBR** ao iniciar e download automático de versões mais novas, em segundo plano, com SHA-256 conferido.
- A atualização baixada é aplicada ao sair pelo menu da bandeja, ou pelo botão **Atualizar agora**. Não há reinício automático durante o uso. Configurações e cache são preservados; uma falha na troca restaura o executável anterior.
- O anúncio brasileiro **`Campeão usou Flash Hextec`** agora confirma o uso do **Flash normal**, com o mesmo nome, ícone e cooldown. Os dois nomes compartilham a deduplicação do mesmo uso.
- Versão interna estampada e ferramenta de release ajustada para reconhecer tags PT-BR e evitar números anteriores à build atual.

Também mantém as mudanças anteriores:

- Interface em Português Brasileiro, mantendo inglês e francês.
- Nomes oficiais brasileiros de campeões, feitiços e ultimates pelo Data Dragon, com os identificadores e o cache preservados.
- Reconhecimento PT-BR, incluindo `Campeão R` e `Campeão usou R`, mantendo as marcações de incerteza e de duração aproximada.
- Cartões fixos agrupados por campeão: retrato acima de ult / Flash / outro feitiço. Pronto aparece com ícone normal; recarga recebe cinza translúcido, X e contador embaixo.
- Cartões permanecem quando tudo fica pronto, até o reset da sessão. Linha do tempo e Linhas compactas preservam seu comportamento.
- Correções de legibilidade dos números, posicionamento pelo guia e encerramento do programa.
- Instalador nativo do Windows com licenças e documentação.

## Validação e limites

- Aplicativo: **37/37 suítes passaram**, incluindo 14 testes novos do ciclo de atualização e oito testes do anúncio de Flash Hextec, além da permanência dos cartões e compatibilidade com inglês/francês.
- Build: **95/95 verificações estáticas passaram**; 19 módulos, incluindo OCR, parser, timers, captura e renderizador, mantêm o código compilado da build local anterior de Flash Hextec.
- Instalador: **44/44 verificações passaram**, incluindo integridade e extração dos 15 arquivos, hashes, tabelas de atalhos/desinstalação e planejamento pelas APIs nativas do Windows.
- Um download real da release anterior foi conferido por tamanho e SHA-256, sem executar o arquivo. A comparação recusou oferecer a versão antiga à build nova.
- Instalação/desinstalação completas do MSI e troca/reinício de um FlashWatch real **não foram executados**. Aplicação e recuperação após falha foram testadas com arquivos fictícios em pastas temporárias.
- Nenhuma partida aberta foi capturada ou controlada nesta validação. A fixture brasileira fornecida anteriormente foi reconhecida parcialmente; localização automática da área de chat e demais formatos ainda têm limitações documentadas. Frases sem evidência continuam identificadas como hipóteses.
- Cooldowns base não foram certificados como atuais; ultimates sem contagem explícita continuam aproximadas.
- O formato do anúncio de Flash Hextec foi relatado pelo usuário, ainda sem captura da nova mensagem. Não há um timer separado de Hexflash de 20 segundos; a interpretação solicitada confirma o Flash comum.
- Binários sem assinatura Authenticode. A preferência existente de desativar a checagem é respeitada; por padrão, a opção fica ativada.
- A atualização automática exige uma release pública estável com versão numérica superior a 1.0.2 e `FlashWatch-PTBR.exe` corretamente estampado e com digest. A versão mostrada em Aplicativos instalados do Windows identifica o MSI e pode permanecer diferente após atualizações do executável.

Relatórios completos em [docs](https://github.com/MiharaxD/flashwatch-PTBR/tree/main/docs). Os arquivos de licença e avisos também acompanham a release e o instalador.

## SHA-256

```text
d8152dd7945c25aac563644b84848b985621f9f1ee1370344683604cab8fa38d  FlashWatch-PTBR-Setup.msi
bb60194556ab1443c6d139c36a9a2e9fd2d9b2101c887c47b5b532aecdc297bf  FlashWatch-PTBR.exe
```

Projeto original: [abenfraj/flashwatch](https://github.com/abenfraj/flashwatch). Esta edição é uma modificação local e não é uma release oficial do projeto original nem um produto endossado pela Riot Games.
