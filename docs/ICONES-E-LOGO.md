# Ícone e logo lateral — revisão 1.0.4

O ícone do executável mantém o desenho e o fundo originais, com cantos arredondados e transparência fora do contorno. O ICO inclui 16, 24, 32, 48, 64, 128 e 256 pixels.

No painel lateral, o logo passa de 76 para 136 unidades, acompanha a escala da janela e fica centralizado horizontalmente. O fundo azul e a moldura circular roxa foram removidos dessa apresentação. Navegação, textos e demais componentes mantêm seu alinhamento anterior.

## Arquivos e reprodução

- Original preservado: `design/brand/flashwatch-logo.png`.
- Fonte recortada: `design/brand/flashwatch-mark-transparent.png`.
- Logo consumido pelo painel: `resources/brand/flashwatch-transparent-512.png`.
- Ícone do executável: `resources/brand/flashwatch.ico`.
- Janela/bandeja continuam usando `resources/brand/flashwatch-round-256.png`.

Para regenerar somente os arquivos do aplicativo, execute `python tools/make_brand.py --app-only`. O script usa o recorte transparente já salvo, sem chamar geração de imagens. O site não foi alterado.

A remoção do fundo foi feita com a ferramenta integrada `image_gen`, usando `resources/brand/flashwatch-512.png` como alvo e transparência habilitada. Prompt utilizado:

> Use case: background-extraction. Edit target: the supplied existing FlashWatch logo. Remove only the dark navy background everywhere, including the large interior of the stopwatch ring and the empty spaces around the clock hands. Output a genuinely transparent RGBA PNG. Preserve exactly the existing stopwatch outline in gold and cyan-blue, gold top button and diagonal side button, gold clock hand and cyan hexagonal hub, original shapes, proportions, colors and fine gold texture. No redesign, no added outlines, no tile, no new shadows, no text, no checkerboard baked in. Keep the entire mark centered on a square transparent canvas, tightly framed with a small safe margin.

## Validação

As páginas do painel e do guia são renderizadas em Qt `offscreen`; a conferência visual usa essas imagens, sem captura da área de trabalho. O teste da janela/bandeja simula a detecção e impede captura real do jogo. Relatórios desta revisão ficam em `build/visual-logo-validation.json`, `build/package-visual-logo-verification.json` e `build/installer/verification.json`.

São verificadas a transparência do logo, a centralização nas escalas da interface, os tamanhos e cantos transparentes do ICO e os arquivos incorporados ao executável. O MSI é extraído e conferido por hashes e planejamento nativo. Não foram executados o aplicativo empacotado, o LoL ou uma instalação/desinstalação completa. Esta revisão é local, sem publicação automática no GitHub.

Resultados: 3/3 testes das páginas/idiomas/guia e 101/101 verificações de janela e bandeja aprovados. A conferência dos recursos e da geometria do logo passou em 46/46 verificações, incluindo os sete ícones gravados no executável. A inspeção estática do pacote passou em 107/107 verificações, com 21 módulos iguais à build 1.0.3.

Prévia renderizada: `build/visual-logo-preview.png`. SHA-256 do executável: `9d4842079692c074d6cb89f78dc9a657428c23d5ecc619241f3fbdb2243d4727`.
