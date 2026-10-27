# Atualizações automáticas — 27/10/2026

Ao iniciar uma cópia empacotada do FlashWatch PT-BR, o programa consulta a última release pública de **MiharaxD/flashwatch-PTBR**, em segundo plano, após o pequeno atraso de inicialização já existente.

## Comportamento

1. Compara a versão publicada com a versão interna do aplicativo.
2. Se houver uma versão mais nova com `FlashWatch-PTBR.exe` e hash SHA-256, baixa o executável automaticamente em segundo plano.
3. Confere tamanho, cabeçalho de executável Windows e SHA-256 informado pelo GitHub antes de aceitar o arquivo.
4. Deixa a atualização pronta. **Não reinicia automaticamente durante o uso.**
5. Ao escolher **Sair do programa** na bandeja, salva as configurações, encerra a captura e aplica a atualização. A próxima abertura usa a versão nova. O botão **Atualizar agora** aplica a cópia baixada e solicita o reinício imediatamente.

Fechar somente a janela continua minimizando para a bandeja, como antes. A aplicação automática acontece quando o processo é encerrado pela ação de sair, não quando a janela é ocultada.

A opção **Verificar e baixar ao iniciar** fica ativada por padrão, respeitando uma preferência já salva de desativação. **Verificar agora** continua disponível. Ignorar uma versão impede sua instalação e descarta o arquivo baixado correspondente; uma próxima versão diferente volta a ser elegível.

Na troca, o executável anterior é renomeado como cópia de recuperação. Uma falha ao colocar o novo arquivo restaura o anterior. Na próxima inicialização, a limpeza já existente remove os arquivos antigos quando possível. Configurações e ícones em `assets` não são substituídos. Fechar durante o download cancela a transferência e preserva o programa atual.

## Origem e versões

- Repositório: [MiharaxD/flashwatch-PTBR](https://github.com/MiharaxD/flashwatch-PTBR).
- Endpoint: `https://api.github.com/repos/MiharaxD/flashwatch-PTBR/releases/latest`.
- Somente o executável com nome exato e URL de download da mesma release desse repositório é aceito. Drafts, prereleases e metadados inválidos são descartados.
- O aplicativo exige o SHA-256 para iniciar a transferência automática. A [API oficial do GitHub](https://docs.github.com/en/rest/releases/assets#get-a-release-asset) fornece esse dado no campo `digest`.
- A versão interna desta build é **1.0.2**, evitando interpretar a release pública antiga 1.0.0 como atualização. A identificação do pacote MSI também é 1.0.2.
- A ferramenta de release reconhece o sufixo `-ptbr` e usa a versão estampada como piso, evitando publicar automaticamente um número mais antigo. Uma próxima release deve ter versão numérica superior, como `v1.0.3-ptbr` ou `v1.0.3`, e conter o executável corretamente estampado.

Não é preciso instalar o MSI a cada atualização: tanto a cópia portátil quanto a instalada atualizam o executável na própria pasta gravável. A versão exibida em Aplicativos instalados do Windows identifica o pacote MSI e pode permanecer diferente da versão interna após atualizações do executável.

As versões antigas que ainda apontam para o projeto original precisam receber esta build uma vez manualmente. A edição nova passa a consultar o repositório brasileiro nas próximas aberturas. Rodar a partir do código-fonte não baixa nem substitui arquivos do checkout.

## Arquivos desta revisão

- `src/updater.py`: repositório brasileiro, validação de URL, digest e download.
- `src/main.py`: download automático, estado pronto, aplicação na saída, cancelamento e ação manual.
- `src/version.py`: versão interna 1.0.2.
- `src/i18n.py`, `src/settings.py`: rótulos e descrição nos três idiomas.
- `tools/release_meta.py`: tags PT-BR e piso da versão publicada.
- `tests/test_auto_update.py`: 14 testes do ciclo de atualização, falhas e versões.
- `tests/test_updater.py`, `tests/test_ptbr_packaging.py`: fixtures de URLs do repositório brasileiro.
- `build_installer.py`, `docs/INSTALADOR.md`: metadados da nova build e do MSI.

## Validação e limites

**37/37 suítes passaram**, incluindo os 14 testes novos de atualização e os testes anteriores de download e rollback. Desempenho: 9/9 verificações; leitura alterada de chat em 774 ms, dentro do limite original de 900 ms. Logs em `build/auto-update-tests/`.

O download real do executável da release pública 1.0.0-ptbr foi conferido por tamanho e SHA-256, sem executá-lo. A comparação também confirmou que essa release antiga não é oferecida para a build 1.0.2. Esse download explícito foi apenas uma validação da transferência; não houve instalação nem downgrade.

A aplicação ao sair e a recuperação após falha foram testadas com arquivos fictícios em pastas temporárias. A substituição de um executável real em uso, o reinício real, a instalação/desinstalação completas do MSI e a interação com uma partida não foram executados. Não houve captura nem controle do LoL.

Uma queda de energia ou encerramento forçado pode impedir a aplicação ao sair; a próxima abertura consulta novamente. Falta de rede, limite da API ou falta de permissão de escrita não impedem o uso do aplicativo atual.

Esta revisão corresponde à [v1.0.2-ptbr](https://github.com/MiharaxD/flashwatch-PTBR/releases/tag/v1.0.2-ptbr). O empacotamento não publica nada automaticamente: a publicação é uma etapa separada. As builds anteriores continuam preservadas, e a identificação final dos arquivos acompanha a nova build.
