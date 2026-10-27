# Janela ao iniciar — revisão 1.0.3

O FlashWatch abre sua janela em toda inicialização, inclusive quando iniciado pelo Windows. Configurações antigas com `open_window_on_launch: false` e atalhos existentes com `--startup` não escondem mais a janela. A opção de iniciar com o Windows continua disponível; a opção de abrir direto na bandeja foi removida.

No primeiro uso, o guia de configuração continua aparecendo. Depois, aparece a janela principal. Fechar no X envia para a bandeja sem encerrar; abrir novamente pelo ícone ou executar outra vez traz a janela de volta. Sair pelo menu da bandeja continua encerrando o programa.

Os textos correspondentes foram atualizados em português, inglês e francês. Configurações existentes são preservadas, incluindo a chave antiga, que passa a ser ignorada. Captura, OCR, overlay, recargas e atualizações mantêm seu comportamento.

## Validação

A suíte `tests/test_app_shell.py` verifica a abertura real da janela Qt em modo `offscreen`, tanto com preferências antigas quanto com inicialização pelo Windows, além de fechar no X, reabrir e preservar o guia inicial. As consultas ao jogo e a captura estão substituídas por simulações; qualquer tentativa de captura real falha no teste.

Relatório das suítes: `build/janela-ao-iniciar-tests/results.json`. Relatório da inspeção estática do executável: `build/package-janela-ao-iniciar-verification.json`. Relatório do MSI: `build/installer/verification.json`.

Resultados: **37/37 suítes** aprovadas, incluindo **101/101 verificações** da janela/bandeja e **9/9 de desempenho**. A inspeção estática do executável passou em **106/106 verificações**, com 18 módulos iguais à build 1.0.2. SHA-256 do executável: `5fce46625e93e57c2e9c6a489f0b80896d464bf52d7ec970ba50c2cc04ea48c8`.

O executável empacotado não é iniciado nesta validação. Não há teste no LoL aberto nem captura de tela do jogo. Instalação e desinstalação completas também não fazem parte desta validação. Esta revisão local não publica uma release automaticamente.
