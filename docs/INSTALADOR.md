# Instalador Windows — FlashWatch PT-BR

O arquivo `FlashWatch-PTBR-Setup.msi` instala a build 1.0.8 com identidade Hextech, janela redimensionável e brilho de cristal nos botões, janela visível ao iniciar, cartões persistentes, reconhecimento de `usou Flash Hextec` como Flash normal confirmado e atualizações automáticas pelo GitHub brasileiro. O empacotamento não recompila nem altera o executável; o SHA-256 é registrado em `build/installer/manifest.json`.

## Instalar

1. Feche a versão antiga do FlashWatch pelo ícone da bandeja.
2. Abra `FlashWatch-PTBR-Setup.msi` e clique em **Instalar**.
3. Se quiser, marque **Criar atalho na área de trabalho**.
4. Depois, abra **FlashWatch PT-BR** pelo menu Iniciar.

A instalação é por usuário, na pasta `%LOCALAPPDATA%\Programs\FlashWatch PT-BR`. Não é necessário instalar Python. O pacote não abre o aplicativo ao concluir, não habilita inicialização automática e não fecha processos por conta própria.

O programa mantém o mecanismo existente de migração de configurações: ao ser aberto pela primeira vez, procura o último local de dados registrado pelo próprio FlashWatch e copia as configurações se ainda não existirem no novo local. A cópia antiga é preservada. O cache de ícones continua sendo baixado pelo aplicativo quando necessário; não são distribuídos configurações, logs, imagens de partida nem dados pessoais desta máquina.

## Desinstalar ou reparar

Use **Aplicativos instalados** do Windows ou **Desinstalar FlashWatch PT-BR** no menu Iniciar. O instalador também oferece reparação ao reabrir o mesmo pacote. Feche o aplicativo pela bandeja antes de reparar ou remover.

Os arquivos instalados e os atalhos são removidos. As configurações e o cache criados pelo aplicativo ficam preservados em sua pasta `assets`; a pasta de instalação poderá permanecer por esse motivo. O pacote não remove a configuração de inicialização automática já gerenciada pelo aplicativo; se você a ativou, desative-a no FlashWatch antes de desinstalar.

## Identidade e licenças

Este é um empacotamento local, não uma release oficial do projeto original. A versão **1.0.4 do MSI** identifica o instalador; o aplicativo também identifica esta build como 1.0.4 para comparar atualizações. O MSI mantém a identidade de atualização desta edição, com uma nova identidade de produto para a revisão.

A licença MIT integral, os avisos da modificação e a licença da fonte Mulish acompanham a instalação. O pacote local não tem assinatura Authenticode nem certificado de editor verificado.

## Reprodução e validação

```powershell
.\.venv\Scripts\python.exe build_installer.py
```

Requer Windows e Python 3.11 apenas na máquina de empacotamento. O script usa a biblioteca nativa `msilib` e o Windows Installer, sem ferramentas de terceiros. Saída: `dist/hextech-1.0.8/instalador/FlashWatch-PTBR-Setup.msi`.

O executável validado é conferido por hash antes de empacotar. A lista explícita de arquivos inclui o programa, as licenças e a documentação; a pasta `assets` não é copiada. O pacote não contém ações personalizadas para iniciar programas.

Os resultados desta revisão são documentados em `docs/ICONES-E-LOGO.md`. O MSI é conferido com extração, hashes e planejamento nativo; instalação/desinstalação completas e execução sobre o LoL continuam fora desta validação. A revisão é local e não altera automaticamente a release pública anterior.

Depois de instalar esta build uma vez, ela verifica o GitHub ao abrir e baixa versões mais novas em segundo plano. A atualização é aplicada ao sair pelo menu da bandeja, ou pelo botão Atualizar agora. Configurações e cache são mantidos; não é preciso instalar o MSI a cada atualização. A preferência existente de desativar a checagem é respeitada.

Referências técnicas: [Windows Installer por usuário](https://learn.microsoft.com/en-us/windows/win32/msi/authoring-packages-without-the-uac-dialog-box), [biblioteca msilib do Python 3.11](https://docs.python.org/3.11/library/msilib.html) e [extração administrativa do MSI](https://learn.microsoft.com/en-us/windows/win32/msi/administrative-installation).
