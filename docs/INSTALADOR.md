# Instalador Windows — FlashWatch PT-BR

O arquivo `FlashWatch-PTBR-Setup.msi` instala a última build local de cartões persistentes. O executável do aplicativo não é recompilado nem alterado: SHA-256 `2a68302e15d94143d3127e98dad18d8e34916e0364146bbdb7b8079ad1cb7d4a`.

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

Este é um empacotamento local, não uma release oficial do projeto original. A versão **1.0.0 do MSI** identifica o instalador e não altera o `0.0.0-dev` embutido no aplicativo original desta build. O MSI usa uma identidade estável para futuras atualizações desta edição.

A licença MIT integral, os avisos da modificação e a licença da fonte Mulish acompanham a instalação. O pacote local não tem assinatura Authenticode nem certificado de editor verificado.

## Reprodução e validação

```powershell
.\.venv\Scripts\python.exe build_installer.py
```

Requer Windows e Python 3.11 apenas na máquina de empacotamento. O script usa a biblioteca nativa `msilib` e o Windows Installer, sem ferramentas de terceiros. Saída: `dist/instalador/FlashWatch-PTBR-Setup.msi`.

O executável validado é conferido por hash antes de empacotar. A lista explícita de arquivos inclui o programa, as licenças e a documentação; a pasta `assets` não é copiada. O pacote não contém ações personalizadas para iniciar programas.

Os resultados específicos do instalador são entregues em `dist/instalador/VALIDACAO-INSTALADOR.md`. A build do aplicativo preserva os resultados anteriores de 35/35 suítes; sua execução sobre o LoL continua deliberadamente fora desta validação.

Referências técnicas: [Windows Installer por usuário](https://learn.microsoft.com/en-us/windows/win32/msi/authoring-packages-without-the-uac-dialog-box), [biblioteca msilib do Python 3.11](https://docs.python.org/3.11/library/msilib.html) e [extração administrativa do MSI](https://learn.microsoft.com/en-us/windows/win32/msi/administrative-installation).
