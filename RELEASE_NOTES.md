# FlashWatch PT-BR 1.0.8 — identidade Hextech

## Novidades

- Nova identidade visual com cronômetro dourado e cristal ciano, artes no início, fontes Beaufort/Spiegel e molduras geométricas.
- Botões com brilho lapidado que percorre o contorno, recuo ao pressionar e pulso luminoso ao confirmar. Respeita a opção do Windows de reduzir animações.
- Janela redimensionável pelas bordas e cantos, com maximização e ajuste de escala.
- Menu lateral com alinhamento e margens corrigidos.
- Cartões de recargas com retrato circular sobreposto, nome do campeão, feitiços quadrados e tempo somente nas habilidades em recarga. Novo posicionamento padrão vertical.
- Janela visível ao iniciar, inclusive com preferências antigas; fechar a janela continua enviando o aplicativo à bandeja.

## Downloads

- **FlashWatch-PTBR-Setup.msi**: instalador Windows por usuário, com atalhos e desinstalação.
- **FlashWatch-PTBR.exe**: versão portátil do mesmo aplicativo.
- **SHA256SUMS.txt**: hashes SHA-256 dos dois arquivos.

Feche a cópia antiga em **Fechar o programa** antes de instalar ou abrir a nova. Não precisa instalar Python.

As posições e preferências existentes são preservadas. Para aplicar a disposição vertical: **Exibição → Cartões fixos → Restaurar posição**.

## Verificação

Interface e recargas conferidas por testes e renderizações Qt; bordas/cantos verificados no Windows. O instalador passou em 47 verificações, incluindo extração e igualdade do executável por SHA-256. Recursos visuais incorporados conferidos.

O aplicativo empacotado não foi testado dentro de uma partida. Os efeitos dos botões não alteram o OCR ou o cálculo das recargas.

**Limitação conhecida de desempenho:** o teste local de OCR reconheceu todas as mensagens, mas a leitura de chat alterado levou 917 ms para um limite de 900 ms (8/9 verificações). O restante das suítes passou, com a expectativa de cartões atualizada para o formato vertical.
