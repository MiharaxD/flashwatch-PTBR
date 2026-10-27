# Identidade Hextech — 1.0.5

## Revisão 1.0.8 — brilho pelo contorno

O reflexo agora percorre a distância do caminho da moldura, virando junto dos
chanfros. Máscara, iluminação interna e pulso usam o mesmo recorte dos cantos
metálicos. Mantidos os tempos, ações e resposta ao clique da 1.0.7.
Seis testes de interação aprovados. Prévia: `build/button-motion/contour-demo.gif`.
Executável local: `dist/hextech-1.0.8/FlashWatch-PTBR.exe`.

## Revisão 1.0.7 — movimento dos botões

Referência: vídeo `screen-capture.webm` fornecido pelo usuário, botão Jogar no
topo esquerdo. A análise dos quadros mostrou contorno azul com reflexo branco
durante o hover e resposta luminosa curta no clique.

Nos botões nativos HexButton, substituídas as facetas triangulares estáticas por
refração no contorno: entrada de brilho em 160 ms, reflexo percorrendo a borda
em 1250 ms, recuo interno de 1,5 px em 80 ms ao pressionar, retorno em 180 ms e
pulso de confirmação de 360 ms. A área clicável e o layout não se movem.
Mouse e teclado acionam os mesmos sinais nativos; soltar fora cancela a ação
sem o pulso. Ocultar/desabilitar interrompe os efeitos. Animações reduzidas do
Windows continuam respeitadas. Os controles de título e o guia pintado conservam
seu comportamento próprio. Não há vibração física nem animação permanente.

Seis testes de interação aprovados em `tests/test_hextech.py`. Demonstração
animada renderizada pelo próprio Qt: `build/button-motion/button-demo.gif`.
Executável: `dist/hextech-1.0.7/FlashWatch-PTBR.exe`. Versões anteriores preservadas.

## Revisão 1.0.6 — fidelidade, navegação e janela

Após a comparação com o mockup aprovado, as molduras ganharam contornos em
camadas, chanfros e losangos; fundos recebem gravações geométricas e círculos.
As artes ficaram mais visíveis e os textos do início em português foram
encurtados. Ícones e títulos do menu agora são posicionados dentro de margens
medidas, em vez de depender do padding ignorado na pintura parcial do Qt.

A janela aceita dimensões livres a partir de 900 × 650, ajusta a escala dos
controles e mantém rolagem nas páginas longas. Maximizar/restaurar usa o estado
nativo. Hit-testing do Windows identifica as bordas e cantos da janela sem
moldura. `tests/test_resizable_shell.py` passou com Qt offscreen e com o backend
Windows: quatro tamanhos e hit-tests nativos de canto e borda, sem workers de
captura/detecção. Os rótulos de navegação em português couberam nos quatro tamanhos.

Cartões fixos: retrato circular sobreposto à borda, losango superior, nome,
ícones quadrados e tempos somente nas recargas. Cores dos tempos desses cartões
seguem creme/âmbar da referência. A máscara continua cinza com X. Outros layouts
mantêm suas cores funcionais. A posição padrão de cartões novos é vertical;
posições já salvas continuam disponíveis (Exibição → Restaurar posição aplica
o novo padrão). Ícones reais do jogo substituem as aproximações do mockup.

Build local: `dist/hextech-1.0.6/FlashWatch-PTBR.exe`. Prévias reais e relatórios
em `build/hextech-refined/`. A versão anterior permanece em sua própria pasta.
O executável empacotado não foi iniciado em uma partida.

---

Aplicação da direção visual aprovada em 27/10/2026. A organização das telas,
ações, detecção e cálculo das recargas permanecem os mesmos.

## Recursos

- Novo original: `design/brand/flashwatch-hextech.png`, RGBA transparente.
  O cronômetro anterior permanece nos arquivos originais de `design/brand/`.
- Artes fornecidas pelo usuário preservadas como `hextech-void.png` e
  `hextech-champions.png` nessa pasta. Versões JPEG para a interface ficam em
  `resources/art/`. A segunda arte tem 400 × 225 pixels de origem: não foi
  substituída por uma reconstrução gerada.
- Spiegel Regular/Bold e Beaufort for LOL Regular/Bold extraídas do pacote de
  fontes fornecido pelo usuário. Os ZIPs fornecidos não contêm arquivo de licença;
  este registro identifica a procedência e não afirma uma licença de redistribuição.
- Os PNGs de runtime e o ICO de sete resoluções são derivados do novo original.
  Reproduzir com `python tools/make_brand.py --app-only`.

## Componentes

`src/theme.py` centraliza cores e fontes: azul profundo, texto creme, bronze e
dourado estrutural, ciano para seleção e energia. Beaufort aparece nos títulos;
Spiegel nos controles e textos. Painel, configurações, ajuda e guia usam a mesma
paleta. As artes são recortadas e recebem transparência gradual atrás dos textos.

`src/hextech.py` mantém o comportamento nativo de QPushButton e pinta as bordas
chanfradas, o relevo e as facetas. Hover e foco por teclado animam em 160 ms;
não há animação contínua. Pressionar reduz a intensidade; desabilitar elimina o
brilho. Ocultar cancela a animação. A preferência de animações de área de cliente
do Windows é respeitada; nesse caso o estado muda imediatamente. Os controles
de janela mantêm a apresentação convencional. O guia reutiliza a pintura de
brilho em seus botões desenhados.

Os cartões do overlay recebem moldura discreta e fundo conforme a opacidade
escolhida. Retratos, slots, X de recarga, tempos, incerteza e cores dos estados
continuam com a lógica existente. Escuro é o padrão para configurações novas;
as preferências já salvas não são migradas nem sobrescritas.

## Validação

- `tests/test_hextech.py`: 4 testes de hover/saída, término da animação, foco,
  acionamento por teclado, desabilitado, movimento reduzido e carregamento de fontes.
- `tests/test_ptbr_ui.py`: 3 testes de telas, idiomas, guia e legibilidade.
- `tests/test_champion_cards.py`: 8 testes de geometria, estados e persistência
  da apresentação dos cartões, incluindo 1080p/1440p e fontes maiores.
- `tests/test_app_shell.py`: 101/101 verificações de janela/bandeja.
- Imagens reais renderizadas pelo Qt em `build/hextech/`, incluindo início,
  exibição, configurações, ajuda e estados normal/hover do botão.

Renderização e testes são offscreen, sem abrir o League nem capturar a área de
trabalho. O executável local fica em `dist/hextech-1.0.5/FlashWatch-PTBR.exe`.
Não há publicação, instalação automática ou substituição da versão em execução.

Build concluída com código 0. A inspeção do executável confirmou os dez recursos
novos/atualizados (PNG, JPEG e fontes) byte a byte e a presença do módulo Hextech.
Relatório: `build/hextech/package-verification.json`. O executável empacotado
não foi iniciado; os testes de funcionamento acima usam o código-fonte.
