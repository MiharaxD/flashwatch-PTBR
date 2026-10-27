"""Every user-facing string, in French, English and Brazilian Portuguese.

One table rather than per-module constants: the point of translating is that a
missing string is *visible*, and a single catalogue makes an untranslated entry
obvious at a glance instead of hiding in whichever file happens to print it.

The language follows the League client language chosen in the settings, because
the two are almost never different in practice -- someone playing on an English
client reads English. It is deliberately not read from Windows: what matters is
the language of the chat being OCR'd, not the one the desktop is in. Until that
choice is made -- first launch, or a locale nobody recognises -- it is English:
the guide that asks the question has to be written in something, and English is
the language the most players will be able to answer it in.

``tr`` never raises. An unknown key comes back as the key itself, which shows up
in the interface as a plain slug instead of crashing the window that was about to
be drawn.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

FRENCH = "fr"
ENGLISH = "en"
PORTUGUESE = "pt"
LANGUAGES = (FRENCH, ENGLISH, PORTUGUESE)

# Riot's locale codes, which are what the data downloader wants.
LOCALES = {FRENCH: "fr_FR", ENGLISH: "en_US", PORTUGUESE: "pt_BR"}

_language = ENGLISH


def language_for(locale: str) -> str:
    """Map supported Riot locales to a language; unknown locales use English.

    pt_PT is deliberately not Brazilian Portuguese. Accept the short picker
    code and the two usual separators for pt_BR without changing saved values.
    """
    value = str(locale).lower().replace("-", "_")
    if value in ("pt", "pt_br"):
        return PORTUGUESE
    return FRENCH if value.startswith("fr") else ENGLISH


def locale_for(language: str) -> str:
    return LOCALES.get(language, LOCALES[ENGLISH])


def set_language(value: str) -> str:
    """Switch language. Accepts a language code or a Riot locale."""
    global _language
    _language = value if value in LANGUAGES else language_for(value)
    return _language


def current() -> str:
    return _language


def tr(key: str, **kwargs) -> str:
    entry = STRINGS.get(key)
    if entry is None:
        log.warning("missing translation for %r", key)
        return key
    text = entry[LANGUAGES.index(_language)]
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            log.warning("bad format arguments for %r", key)
    return text


# (French, English, Brazilian Portuguese)
STRINGS: dict[str, tuple[str, str, str]] = {
    # -- window titles ---------------------------------------------------
    "app.title": ("Flashwatch", "Flashwatch",
        "Flashwatch"),
    "app.tray_tooltip": ("Flashwatch",
                         "Flashwatch",
        "Flashwatch"),
    "app.already_running": (
        "Flashwatch est deja lance : cherchez son icone dans la zone de "
        "notification, en bas a droite (eventuellement sous la fleche). Deux "
        "copies se disputeraient l'overlay.",
        "Flashwatch is already running: look for its icon in the notification "
        "area at the bottom right (possibly under the arrow). Two copies would "
        "fight over the overlay.",
        "O Flashwatch já está aberto: procure o ícone na área de notificação, no canto inferior direito (talvez dentro da setinha). Duas cópias disputariam o overlay."),

    # -- game state ------------------------------------------------------
    "game.in_game": ("En jeu ({width}x{height})", "In game ({width}x{height})",
        "Em partida ({width}x{height})"),
    "game.client_only": ("Client ouvert, pas en partie",
                         "Client open, not in a game",
        "Cliente aberto, fora de partida"),
    "game.absent": ("League of Legends non detecte",
                    "League of Legends not detected",
        "League of Legends não detectado"),

    # -- start-up / Riot data -------------------------------------------
    "boot.loading": ("Chargement des donnees Riot...", "Loading Riot data...",
        "Carregando dados da Riot..."),
    "boot.error": ("Erreur de chargement : {error}", "Loading failed: {error}",
        "Falha no carregamento: {error}"),
    "boot.waiting": ("En attente de League of Legends...",
                     "Waiting for League of Legends...",
        "Aguardando League of Legends..."),
    "assets.version": ("Recherche de la version du patch...",
                       "Looking up the patch version...",
        "Consultando a versão da atualização..."),
    "assets.patch": ("Patch {version} - chargement des donnees ({locale})",
                     "Patch {version} - loading data ({locale})",
        "Atualização {version} - carregando dados ({locale})"),
    "assets.spells": ("{count} sorts d'invocateur charges",
                      "{count} summoner spells loaded",
        "{count} feitiços de invocador carregados"),
    "assets.champions": ("{count} champions charges", "{count} champions loaded",
        "{count} campeões carregados"),
    "assets.icons_cached": ("Icones deja en cache", "Icons already cached",
        "Ícones já estão no cache"),
    "assets.icons_downloading": ("Telechargement de {count} icones...",
                                 "Downloading {count} icons...",
        "Baixando {count} ícones..."),
    "assets.icons_progress": ("Icones {done}/{total}", "Icons {done}/{total}",
        "Ícones {done}/{total}"),
    "assets.offline": (
        "Impossible de contacter Data Dragon et aucun cache local n'existe. "
        "Verifiez votre connexion internet au premier lancement.",
        "Data Dragon is unreachable and there is no local cache. Check your "
        "internet connection for the first run.",
        "Não foi possível acessar o Data Dragon e não há cache local. Confira sua conexão com a internet no primeiro uso."),

    # -- overlay ---------------------------------------------------------
    "overlay.enemy_spells": ("SORTS ENNEMIS", "ENEMY SPELLS",
        "FEITIÇOS INIMIGOS"),
    "overlay.unlocked": ("deverrouille", "unlocked",
        "destravado"),
    "overlay.unlocked_hint": ("Flashwatch - deverrouille, glissez pour deplacer",
                              "Flashwatch - unlocked, drag to move",
        "Flashwatch - destravado, arraste para mover"),
    "overlay.waiting": ("En attente...", "Waiting...",
        "Aguardando..."),
    "overlay.nothing_yet": ("Aucun sort detecte pour le moment",
                            "No spell detected yet",
        "Nenhum feitiço detectado ainda"),

    # -- tray menu -------------------------------------------------------
    "tray.overlay": ("Afficher l'overlay", "Show the overlay",
        "Mostrar overlay"),
    "tray.lock": ("Verrouiller (clics traversants)",
                  "Lock (click-through)",
        "Travar (permitir cliques através)"),
    "tray.test_mode": ("Mode test : placer la zone OCR",
                       "Test mode: place the OCR zone",
        "Modo de teste: posicionar área de OCR"),
    "tray.settings": ("Parametres...", "Settings...",
        "Configurações..."),
    "tray.guide": ("Guide d'installation...", "Setup guide...",
        "Guia de configuração..."),
    # No longer "at the top": each display has its own default place, and the
    # rows belong down a side.
    "tray.recentre": ("Remettre l'affichage en place",
                      "Put the display back in place",
        "Restaurar posição do overlay"),
    "tray.demo": ("Essayer sans partie", "Try it without a game",
        "Experimentar sem entrar em partida"),
    "tray.redetect": ("Redetecter le chat", "Detect the chat again",
        "Detectar o chat novamente"),
    "tray.reset": ("Reinitialiser les timers", "Reset the timers",
        "Zerar temporizadores"),
    "tray.quit": ("Quitter (fermer le programme)", "Quit (close the program)",
        "Sair (fechar o programa)"),
    "notify.zone_saved": ("Zone OCR enregistree ({width}x{height}).",
                          "OCR zone saved ({width}x{height}).",
        "Área de OCR salva ({width}x{height})."),
    "notify.bar_in_game_only": (
        "La barre s'affichera automatiquement des que vous serez en partie.",
        "The bar will appear by itself once you are in a game.",
        "A barra aparecerá automaticamente quando você estiver em partida."),
    "notify.demo_ended": (
        "Une partie a demarre : le mode essai s'arrete et l'affichage repasse en "
        "clics traversants.",
        "A game has started: the trial stops and the display goes back to "
        "click-through.",
        "Uma partida começou: a demonstração terminou e o overlay voltou a permitir cliques através dele."),
    "notify.demo_loading": (
        "Les donnees Riot finissent de se telecharger. Reessayez dans quelques "
        "secondes.",
        "Riot's data is still downloading. Try again in a few seconds.",
        "Os dados da Riot ainda estão sendo baixados. Tente novamente em alguns segundos."),
    "notify.hidden_to_tray": (
        "Flashwatch continue de tourner ici. Double-cliquez sur l'icone pour "
        "rouvrir les reglages, ou clic droit puis Quitter pour fermer le "
        "programme.",
        "Flashwatch is still running here. Double-click the icon to reopen the "
        "settings, or right-click then Quit to close the program.",
        "O Flashwatch continua funcionando aqui. Clique duas vezes no ícone para abrir as configurações, ou clique com o botão direito e escolha Sair para fechar o programa."),

    # -- updates ---------------------------------------------------------
    "update.available": ("Flashwatch {version} est disponible.",
                         "Flashwatch {version} is available.",
        "Flashwatch {version} disponível."),
    "update.banner": ("Nouvelle version disponible : {version} "
                      "(vous avez la {current}).",
                      "New version available: {version} "
                      "(you have {current}).",
        "Nova versão disponível: {version} (você usa a {current})."),
    "update.install": ("Mettre a jour maintenant", "Update now",
        "Atualizar agora"),
    "update.notes": ("Voir les nouveautes", "See what changed",
        "Ver novidades"),
    "update.skip": ("Ignorer cette version", "Skip this version",
        "Ignorar esta versão"),
    "update.downloading": ("Telechargement... {percent}%",
                           "Downloading... {percent}%",
        "Baixando... {percent}%"),
    "update.installing": ("Installation...", "Installing...",
        "Instalando..."),
    "update.ready_exit": (
        "Mise a jour telechargee. Elle sera appliquee a la fermeture, ou cliquez sur Mettre a jour maintenant.",
        "Update downloaded. It will be applied when you quit, or click Update now.",
        "Atualização baixada. Será aplicada ao sair, ou clique em Atualizar agora."),
    "update.no_hash": (
        "La release ne fournit pas de SHA-256 pour verifier le programme.",
        "The release does not provide a SHA-256 hash to verify the program.",
        "A release não fornece um hash SHA-256 para conferir o programa."),
    "update.bad_hash": (
        "Le SHA-256 du telechargement ne correspond pas a celui de la release.",
        "The download's SHA-256 does not match the release.",
        "O SHA-256 do download não corresponde ao da release."),
    "update.restarting": (
        "Mise a jour installee. Flashwatch redemarre.",
        "Update installed. Flashwatch is restarting.",
        "Atualização instalada. Reiniciando o Flashwatch."),
    "update.restart_manually": (
        "Mise a jour installee. Relancez Flashwatch pour l'utiliser.",
        "Update installed. Start Flashwatch again to use it.",
        "Atualização instalada. Abra o Flashwatch novamente para usá-la."),
    "update.failed": ("La mise a jour a echoue : {error}",
                      "The update failed: {error}",
        "Falha na atualização: {error}"),
    "update.failed_hint": (
        "Vous pouvez toujours telecharger la nouvelle version depuis la page "
        "des releases.",
        "You can still download the new version from the releases page.",
        "Você ainda pode baixar a nova versão pela página de lançamentos."),
    "update.read_only": (
        "Flashwatch ne peut pas s'ecrire dans {folder}. Telechargez la nouvelle "
        "version a la main, ou deplacez le programme dans un dossier a vous.",
        "Flashwatch cannot write to {folder}. Download the new version by hand, "
        "or move the program to a folder of your own.",
        "O Flashwatch não pode gravar em {folder}. Baixe a nova versão manualmente ou mova o programa para uma pasta sua."),
    "update.keeps_settings": (
        "Vos reglages et les icones deja telechargees sont conserves : ils "
        "vivent dans le dossier assets, pas dans l'executable. L'ancienne "
        "version est supprimee, il ne reste qu'un seul fichier.",
        "Your settings and the icons already downloaded are kept: they live in "
        "the assets folder, not inside the executable. The old version is "
        "removed, so only one file is left.",
        "Suas configurações e os ícones baixados são preservados: eles ficam na pasta assets, fora do executável. A versão anterior é removida, deixando apenas um arquivo."),

    # -- control window: header, navigation, footer -----------------------
    "ui.tagline": ("Timers des sorts ennemis, lus a l'ecran",
                   "Enemy spell cooldowns, read off the screen",
        "Tempos de recarga inimigos, lidos na tela"),
    "ui.nav_home": ("Accueil", "Home",
        "Início"),
    "ui.nav_display": ("Affichage", "Display",
        "Exibição"),
    "ui.nav_settings": ("Reglages", "Settings",
        "Configurações"),
    "ui.nav_help": ("Depannage", "Troubleshooting",
        "Ajuda"),
    "ui.hide_window": ("Masquer la fenetre", "Hide this window",
        "Ocultar janela"),
    "ui.hide_window_tip": (
        "Le programme continue de tourner dans la zone de notification, en bas "
        "a droite. Double-cliquez sur son icone pour revenir ici.",
        "The program keeps running in the notification area, bottom right. "
        "Double-click its icon to come back here.",
        "O programa continua funcionando na área de notificação, no canto inferior direito. Clique duas vezes no ícone para voltar aqui."),
    "ui.quit": ("Quitter (fermer le programme)", "Quit (close the program)",
        "Sair (fechar o programa)"),
    # The same action, said shorter: in the side rail there is no room for the
    # parenthesis, and none needed either -- the rail button sits under "Masquer
    # la fenetre", so the difference between the two is already the sentence.
    "ui.quit_rail": ("Quitter le programme", "Quit the program",
        "Fechar o programa"),

    # -- the live state pill ----------------------------------------------
    "ui.pill_in_game": ("EN PARTIE", "IN GAME",
        "EM PARTIDA"),
    "ui.pill_client": ("CLIENT OUVERT", "CLIENT OPEN",
        "CLIENTE ABERTO"),
    "ui.pill_waiting": ("EN ATTENTE", "WAITING",
        "AGUARDANDO"),
    "ui.pill_loading": ("CHARGEMENT", "LOADING",
        "CARREGANDO"),
    "ui.pill_error": ("PROBLEME", "PROBLEM",
        "PROBLEMA"),
    "ui.pill_demo": ("ESSAI", "TRIAL",
        "DEMONSTRAÇÃO"),

    # -- home page --------------------------------------------------------
    "ui.state_game": ("Jeu :", "Game:",
        "Jogo:"),
    "ui.state_region": ("Zone de chat :", "Chat area:",
        "Área do chat:"),
    "ui.state_ocr": ("OCR :", "OCR:",
        "OCR:"),
    "ui.state_timers": ("Timers actifs :", "Active timers:",
        "Recargas ativas:"),
    "ui.state_clock": ("Horloge estimee :", "Estimated clock:",
        "Relógio estimado:"),
    "ui.home_headline_idle": ("Rien a faire : lancez une partie",
                              "Nothing to do: start a game",
        "Tudo pronto para a próxima partida"),
    "ui.home_headline_idle_hint": (
        "Flashwatch attend en arriere-plan. La barre apparaitra toute seule des "
        "que l'ecran de jeu s'affiche, et se remplira au premier sort ennemi. "
        "Pour voir tout de suite a quoi elle ressemble et la placer : Affichage, "
        "puis \"Afficher des sorts d'exemple\".",
        "Flashwatch waits in the background. The bar shows up by itself once the "
        "in-game screen does, and fills in on the first enemy spell. To see what "
        "it looks like right now and place it: Display, then \"Show sample "
        "cooldowns\".",
        "As recargas inimigas aparecem quando o chat é lido."),
    "ui.home_headline_live": ("En train de lire votre chat",
                              "Reading your chat right now",
        "Lendo seu chat agora"),
    "ui.home_headline_live_hint": (
        "Chaque sort annonce dans le chat demarre un compte a rebours. Vous "
        "n'avez aucune touche a presser.",
        "Every spell announced in chat starts a countdown. There is no key for "
        "you to press.",
        "Cada habilidade anunciada no chat inicia uma contagem regressiva. Você não precisa apertar nenhuma tecla."),
    "ui.home_headline_demo": ("Mode essai : ce que vous voyez est faux",
                             "Trial mode: what you see is not real",
        "Demonstração: os dados são de exemplo"),
    "ui.home_headline_demo_hint": (
        "Des sorts d'exemple sont affiches pour que vous puissiez juger et placer "
        "l'affichage. Rien n'est lu a l'ecran pour l'instant, et tout s'effacera "
        "quand une vraie partie demarrera.",
        "Sample cooldowns are on screen so you can judge and place the display. "
        "Nothing is being read from the screen right now, and it all clears when a "
        "real game starts.",
        "Recargas de exemplo aparecem para você avaliar e posicionar o overlay. Nada está sendo lido da tela agora, e os exemplos somem quando uma partida real começar."),
    "ui.home_headline_boot": ("Preparation en cours",
                              "Getting ready",
        "Preparando tudo"),
    "ui.home_headline_boot_hint": (
        "Les donnees Riot (noms et icones) se telechargent une seule fois, au "
        "premier lancement.",
        "Riot's data (names and icons) downloads once, on the first run.",
        "Os dados da Riot (nomes e ícones) são baixados uma vez, no primeiro uso."),
    "ui.guide_card": ("Guide d'installation", "Setup guide",
        "Guia de configuração"),
    "ui.guide_card_hint": (
        "Trois minutes : mode d'affichage de League, langue du client, cadrage "
        "du chat, position de la barre.",
        "Three minutes: League's display mode, your client language, framing the "
        "chat, and where the bar sits.",
        "Configure o idioma, o chat e a posição do overlay."),
    "ui.guide_open": ("Ouvrir le guide", "Open the guide",
        "Abrir guia"),
    "ui.test_card": ("Test", "Test",
        "Teste"),
    "ui.test_hint": (
        "Une vraie image de partie est fournie avec le programme. Le test la lit "
        "de bout en bout (recherche du chat, OCR, reconnaissance des sorts) et "
        "demarre les timers correspondants, sans attendre de partie.",
        "A real game frame ships with the program. The test reads it end to end "
        "(finding the chat, OCR, recognising the spells) and starts the matching "
        "timers, with no game needed.",
        "Teste a leitura com a captura incluída no programa."),
    "ui.test_run": ("Lancer le test", "Run the test",
        "Executar teste"),
    "ui.test_again": ("Relancer le test", "Run the test again",
        "Repetir teste"),
    "ui.test_running": ("Lecture de l'image...", "Reading the image...",
        "Lendo imagem..."),
    "ui.test_not_ready": (
        "Les donnees Riot finissent de charger. Reessayez dans un instant.",
        "Riot's data is still loading. Try again in a moment.",
        "Os dados da Riot ainda estão carregando. Tente novamente em instantes."),
    "ui.test_pass": ("La chaine de lecture fonctionne.",
                     "The reading chain works.",
        "A cadeia de leitura está funcionando."),
    "ui.test_fail_region": (
        "Le chat n'a pas ete localise dans l'image. C'est la detection de zone "
        "qui est en cause, pas votre configuration.",
        "The chat was not located in the image. That points at the area "
        "detection, not at your setup.",
        "O chat não foi localizado na imagem. Isso indica um problema na detecção da área, sem relação com sua configuração."),
    "ui.test_fail_parse": (
        "Le texte a bien ete lu, mais aucun sort n'y a ete reconnu.",
        "The text was read, but no spell was recognised in it.",
        "O texto foi lido, mas nenhuma habilidade foi reconhecida."),
    "ui.test_fail_partial": (
        "Une partie seulement des sorts attendus a ete reconnue.",
        "Only some of the expected spells were recognised.",
        "Apenas parte das habilidades esperadas foi reconhecida."),
    "ui.test_error": ("Le test n'a pas pu tourner : {error}",
                      "The test could not run: {error}",
        "Não foi possível executar o teste: {error}"),
    "ui.test_detail": (
        "Zone trouvee {region}, {lines} lignes lues dont {chat} reconnues comme "
        "du chat, {ms:.0f} ms",
        "Area found {region}, {lines} lines read of which {chat} recognised as "
        "chat, {ms:.0f} ms",
        "Área encontrada {region}, {lines} linhas lidas, {chat} reconhecidas como chat, {ms:.0f} ms"),
    "ui.test_hit": ("{champion} - {spell} : timer demarre ({time})",
                    "{champion} - {spell}: timer started ({time})",
        "{champion} - {spell}: temporizador iniciado ({time})"),
    "ui.test_hit_existing": ("{champion} - {spell} : reconnu, timer deja en cours",
                             "{champion} - {spell}: recognised, timer already running",
        "{champion} - {spell}: reconhecido, temporizador já ativo"),
    "ui.test_miss": ("{champion} - {spell} : non reconnu",
                     "{champion} - {spell}: not recognised",
        "{champion} - {spell}: não reconhecido"),
    "ui.test_scope": (
        "Ce test ne lit pas votre ecran : il ne peut donc pas confirmer que la "
        "capture de votre partie fonctionne. Pour ca, utilisez Cadrer le chat "
        "pendant une partie, dans Depannage.",
        "This test does not read your screen, so it cannot confirm that capturing "
        "your own game works. For that, use Frame the chat during a game, under "
        "Troubleshooting.",
        "Este teste usa uma captura inglesa e não lê sua tela, portanto não valida a captura da sua partida nem o cliente brasileiro. Para conferir sua partida, use Enquadrar chat em Ajuda."),
    "ui.copy": ("Copier", "Copy",
        "Copiar"),
    "ui.enemies": ("Ennemis reperes", "Enemies spotted",
        "Inimigos identificados"),
    "ui.ocr_summary": ("{runs} analyses, {ms:.0f} ms, {skipped:.0f}% ignorees",
                       "{runs} reads, {ms:.0f} ms, {skipped:.0f}% skipped",
        "{runs} leituras, {ms:.0f} ms, {skipped:.0f}% ignoradas"),
    "ui.redetect": ("Redetecter le chat", "Detect the chat again",
        "Detectar o chat novamente"),
    "ui.manual_region": ("Definir la zone manuellement", "Set the area by hand",
        "Definir área manualmente"),
    "ui.forget_region": ("Oublier la zone enregistree", "Forget the saved area",
        "Esquecer área salva"),
    "ui.reset_timers": ("Reinitialiser les timers", "Reset the timers",
        "Zerar temporizadores"),
    "ui.test_mode": ("Cadrer le chat", "Frame the chat",
        "Enquadrar chat"),
    "ui.test_mode_tip": (
        "Affiche un cadre autour de la zone lue. Deplacez-le pendant la partie : "
        "l'OCR suit le cadre et indique ce qu'il lit.",
        "Draws a frame around the area being read. Move it during a game: the "
        "OCR follows the frame and reports what it reads.",
        "Mostra uma moldura ao redor da área lida. Mova-a durante a partida: o OCR acompanha a moldura e mostra o que lê."),
    "ui.test_mode_clock": ("Cadrer le temps de partie",
                           "Frame the game clock",
        "Enquadrar relógio da partida"),
    "ui.test_mode_clock_tip": (
        "Placez le cadre sur le chronometre de la partie, en haut de l'ecran. "
        "Une fois valide, l'application lit l'heure du jeu directement au lieu "
        "de la deduire des horodatages du chat.",
        "Put the frame over the match timer at the top of the screen. Once "
        "applied, the app reads the game clock directly instead of inferring it "
        "from chat timestamps.",
        "Posicione a moldura sobre o tempo da partida no alto da tela. Depois de aplicar, o programa lê o relógio diretamente, sem depender dos horários do chat."),
    "ui.test_mode_scoreboard": ("Cadrer les ennemis (scoreboard)",
                                "Frame the enemies (scoreboard)",
        "Enquadrar inimigos (placar)"),
    "ui.test_mode_scoreboard_tip": (
        "Maintenez Tab, puis placez le cadre sur la colonne des cinq portraits "
        "ennemis. Chaque portrait est compare aux icones deja telechargees, et "
        "sa position dans la colonne donne le role.",
        "Hold Tab, then put the frame over the column of five enemy portraits. "
        "Each portrait is compared with the icons already downloaded, and its "
        "position in the column gives the role.",
        "Segure Tab e posicione a moldura na coluna dos cinco retratos inimigos. Cada retrato é comparado aos ícones já baixados, e sua posição na coluna indica a função."),
    "ui.test_mode_loading": ("Cadrer l'ecran de chargement",
                             "Frame the loading screen",
        "Enquadrar tela de carregamento"),
    "ui.test_mode_loading_tip": (
        "Placez le cadre sur la rangee des cinq ennemis, pendant le chargement. "
        "Les noms de champions y sont ecrits, et leur ordre donne les roles : "
        "top, jungle, mid, adc, support.",
        "Put the frame over the row of five enemies while the game loads. Their "
        "champion names are printed there, and their order gives the roles: top, "
        "jungle, mid, adc, support.",
        "Posicione a moldura sobre os cinco inimigos enquanto a partida carrega. Os nomes dos campeões aparecem ali e a ordem indica as funções: topo, selva, meio, atirador e suporte."),
    "ui.show_overlay": ("Afficher l'overlay", "Show the overlay",
        "Mostrar overlay"),
    "ui.locked": ("Verrouille (clics traversants)", "Locked (click-through)",
        "Travado (permitir cliques através)"),
    "ui.locked_hint": (
        "Verrouillee, la barre laisse passer les clics vers le jeu et ne peut "
        "pas prendre le focus. Decochez pour la deplacer.",
        "Locked, the bar lets clicks through to the game and can never take "
        "focus. Untick it to move the bar.",
        "Travada, a barra deixa os cliques passarem para o jogo e nunca recebe foco. Desmarque para movê-la."),
    "ui.borderless_tip": (
        "Astuce : jouez en mode fenetre sans bordure. En plein ecran exclusif, "
        "Windows empeche tout overlay de s'afficher.",
        "Tip: play in borderless windowed mode. In exclusive fullscreen, Windows "
        "prevents any overlay from being drawn.",
        "Dica: jogue no modo de janela sem bordas. Em tela cheia exclusiva, o Windows impede a exibição de overlays."),

    # -- display page: choosing and placing the overlay -------------------
    "ui.display_choose": ("Choisissez votre affichage",
                          "Pick the display you prefer",
        "Escolha sua exibição preferida"),
    "ui.display_choose_hint": (
        "Les trois montrent exactement la meme information. Prenez celui que "
        "votre oeil lit le plus vite en combat.",
        "All three show exactly the same information. Take the one your eye reads "
        "fastest in a fight.",
        "As três mostram as mesmas informações. Escolha a que você lê mais rápido durante uma luta."),
    "ui.layout_bar": ("Barre chrono", "Chrono track",
        "Linha do tempo"),
    "ui.layout_bar_hint": (
        "L'icone entre a gauche au lancement du sort et arrive a droite quand il "
        "revient : la position dit tout, sans lire les chiffres.",
        "The icon enters on the left when the spell is cast and reaches the right "
        "as it comes back: position alone tells you, without reading numbers.",
        "O ícone entra pela esquerda quando a habilidade é usada e chega à direita quando volta: a posição já informa o estado, sem ler números."),
    "ui.layout_cards": ("Cartes fixes", "Fixed cards",
        "Cartões fixos"),
    "ui.layout_cards_hint": (
        "Un portrait par champion : ultime a gauche, Flash au centre, autre sort a droite. "
        "Pret : icone normale ; recharge : voile gris et X, avec le temps dessous. Sans temps observe, le sort est suppose pret.",
        "One portrait per champion: ultimate left, Flash centre, other spell right. "
        "Ready: normal icon; cooldown: grey veil and X, with the time below. Without an observed cooldown, readiness is assumed.",
        "Um retrato por campeão: ult à esquerda, Flash no meio e outro feitiço à direita. Pronto: ícone normal. Em recarga: cinza translúcido e X, com o tempo embaixo. Sem recarga registrada, é considerado pronto."),
    "ui.layout_list": ("Rangées compactes", "Compact rows",
        "Linhas compactas"),
    "ui.layout_list_hint": (
        "Une ligne par sort : champion, sort, temps restant et une jauge de "
        "progression. Le plus lisible, le plus haut.",
        "One row per spell: champion, spell, time left and a progress gauge. The "
        "most readable, and the tallest.",
        "Uma linha por habilidade: campeão, habilidade, tempo restante e barra de progresso. É a mais legível e ocupa mais altura."),
    "ui.position": ("Position a l'ecran", "Where it sits on screen",
        "Posição na tela"),
    "ui.position_hint": (
        "L'affichage se pose ou vous voulez : glissez-le n'importe ou, "
        "redimensionnez-le par le coin en bas a droite. Chaque affichage garde sa "
        "propre position.",
        "The display goes wherever you want: drag it anywhere, resize it from the "
        "bottom-right corner. Each display keeps its own position.",
        "O overlay fica onde você quiser: arraste para mover e redimensione pelo canto inferior direito. Cada exibição mantém sua própria posição."),
    "ui.move_start": ("Deplacer / redimensionner", "Move / resize",
        "Mover / redimensionar"),
    "ui.move_done": ("J'ai fini, verrouiller", "Done, lock it",
        "Pronto, travar"),
    "ui.move_active": (
        "Deverrouille : glissez la barre ou vous voulez, tirez le coin en bas a "
        "droite pour la taille, puis revenez verrouiller.",
        "Unlocked: drag the bar wherever you like, pull the bottom-right corner "
        "to resize, then come back and lock it.",
        "Destravado: arraste a barra, puxe o canto inferior direito para redimensionar e volte aqui para travar."),
    "ui.advanced": ("Options avancees", "Advanced options",
        "Opções avançadas"),

    # -- settings tab ----------------------------------------------------
    "ui.language": ("Langue du client", "Client language",
        "Idioma do cliente"),
    "ui.language_fr": ("Francais (client FR)", "French (FR client)",
        "Francês (cliente FR)"),
    "ui.language_en": ("Anglais (client EN)", "English (EN client)",
        "Inglês (cliente EN)"),
    "ui.language_tip": (
        "Langue du client League : elle decide des textes recherches dans le "
        "chat et des noms de champions et de sorts telecharges. L'interface "
        "suit le meme choix.",
        "Your League client's language: it decides which chat wordings are "
        "looked for and which champion and spell names are downloaded. The "
        "interface follows the same choice.",
        "O idioma do seu cliente League define os formatos de mensagem reconhecidos no chat e os nomes de campeões e habilidades baixados. A interface segue a mesma escolha."),
    "ui.language_reloading": (
        "Langue changee. Donnees Riot rechargees en arriere-plan.",
        "Language changed. Riot data is reloading in the background.",
        "Idioma alterado. Recarregando dados da Riot em segundo plano."),
    "ui.appearance": ("Apparence", "Appearance",
        "Aparência"),
    "ui.hide_until_in_game": ("Afficher seulement pendant la partie",
                              "Show only during a game",
        "Mostrar apenas em partida"),
    "ui.hide_until_in_game_tip": (
        "La barre reste invisible sur le bureau et dans le client. Elle "
        "apparait des que l'ecran de jeu est affiche (et reste visible quand "
        "l'overlay est deverrouille, pour pouvoir la deplacer).",
        "The bar stays off the desktop and the client. It appears as soon as the "
        "in-game screen does (and is always shown while the overlay is unlocked, "
        "so it can be moved).",
        "A barra fica oculta na área de trabalho e no cliente. Ela aparece quando a tela da partida abre (e fica visível enquanto destravada, para você posicioná-la)."),
    "ui.bar_when_idle": ("Garder la barre visible au repos",
                        "Keep the bar visible at rest",
        "Manter a barra visível sem recargas"),
    "ui.bar_when_idle_hint": (
        "Sans cela, la barre est totalement invisible quand aucun sort n'est en "
        "recharge : plus discret, mais aucun signe que le programme tourne.",
        "Without it the bar is completely invisible while nothing is on "
        "cooldown: more discreet, but no sign the program is running.",
        "Sem esta opção, a barra some quando não há recargas ativas: mais discreto, mas sem indicar que o programa está funcionando."),
    "ui.bar_vertical": ("Barre chronologique verticale",
                        "Vertical timeline",
        "Linha do tempo vertical"),
    "ui.bar_vertical_hint": (
        "La barre se dresse sur le cote de l'ecran : les recharges descendent "
        "de haut en bas, le temps restant s'affiche a cote de chaque champion. "
        "Elle garde sa propre position, distincte de la barre horizontale.",
        "The bar stands up along the side of the screen: cooldowns run from top "
        "to bottom and the time left sits beside each champion. It keeps its own "
        "position, separate from the horizontal bar.",
        "A barra fica na lateral da tela: as recargas avançam de cima para baixo e o tempo restante aparece ao lado de cada campeão. Ela mantém uma posição própria, separada da barra horizontal."),
    "ui.recentre": ("Remettre en place", "Put it back",
        "Restaurar posição"),
    "ui.recentre_tip": (
        "Replace l'affichage courant a sa position par defaut. Utile apres un "
        "changement de resolution ou d'ecran.",
        "Puts the current display back at its default spot. Useful after changing "
        "resolution or monitor.",
        "Restaura a posição padrão da exibição atual. Útil depois de trocar a resolução ou o monitor."),

    # -- trial mode -------------------------------------------------------
    "ui.demo": ("Essayer sans lancer de partie", "Try it without starting a game",
        "Experimentar sem iniciar uma partida"),
    "ui.demo_hint": (
        "Des sorts d'exemple s'affichent en continu, dans tous les etats : "
        "fraichement lance, a mi-course, bientot pret, deja dispo. De quoi "
        "comparer les trois affichages, essayer un theme et poser la barre ou "
        "vous voulez. Ca s'arrete tout seul quand une vraie partie demarre.",
        "Sample cooldowns stay on screen in every state: just cast, halfway, "
        "nearly back, already up. Enough to compare the three displays, try a "
        "theme and put the bar where you want it. It stops by itself when a real "
        "game starts.",
        "Recargas de exemplo aparecem em todos os estados: recém-usada, pela metade, quase pronta e disponível. Compare as três exibições, escolha um tema e posicione a barra. A demonstração termina quando uma partida real começa."),
    "ui.demo_start": ("Afficher des sorts d'exemple", "Show sample cooldowns",
        "Mostrar recargas de exemplo"),
    "ui.demo_stop": ("Arreter l'essai", "Stop the trial",
        "Encerrar demonstração"),
    "ui.theme": ("Theme :", "Theme:",
        "Tema:"),
    "ui.theme_dark": ("Sombre", "Dark",
        "Escuro"),
    "ui.theme_light": ("Clair", "Light",
        "Claro"),
    "ui.theme_neon": ("Neon", "Neon",
        "Neon"),
    "ui.opacity": ("Opacite :", "Opacity:",
        "Opacidade:"),
    "ui.scale": ("Echelle :", "Scale:",
        "Escala:"),
    "ui.timer_font": ("Police du chrono :", "Timer font:",
        "Fonte da contagem:"),
    "ui.timer_font_auto": ("Automatique", "Automatic",
        "Automática"),
    "ui.timer_font_tip": (
        "Ne concerne que le compte a rebours, pas les noms. Automatique prend la "
        "meilleure police presente sur cette machine : des chiffres de largeur "
        "fixe, pour que le nombre ne tressaute pas a chaque seconde.",
        "Affects the countdown only, never the names. Automatic takes the best "
        "face present on this machine: fixed-width digits, so the number does "
        "not twitch on every tick.",
        "Afeta apenas a contagem, sem alterar os nomes. Automática escolhe a melhor fonte disponível nesta máquina, com dígitos de largura fixa para o número não ficar pulando."),
    "ui.timer_size": ("Taille du chrono :", "Timer size:",
        "Tamanho da contagem:"),
    "ui.timer_size_tip": (
        "Taille du compte a rebours, independamment de l'echelle generale : de "
        "quoi garder de grands portraits avec un nombre discret, ou l'inverse. "
        "Les lignes se redimensionnent avec lui.",
        "Size of the countdown, separately from the overall scale: enough to keep "
        "large portraits with a discreet number, or the other way round. The rows "
        "resize with it.",
        "Tamanho da contagem, independente da escala geral: permite retratos grandes com números discretos ou o contrário. As linhas se ajustam junto."),
    "ui.sort_by_role": ("Trier par role", "Sort by role",
        "Ordenar por função"),
    "ui.hide_ready": ("Masquer les sorts disponibles", "Hide spells that are up",
        "Ocultar habilidades disponíveis"),
    "ui.ready_linger": ("Garder READY affiche :", "Keep READY on screen:",
        "Manter PRONTO na tela:"),
    "ui.ready_linger_tip": (
        "Duree pendant laquelle un sort revenu affiche READY avant que sa ligne "
        "disparaisse. 0 la fait disparaitre des qu'il est pret.",
        "How long a spell that is back up keeps showing READY before its entry "
        "disappears. 0 removes it as soon as it is ready.",
        "Por quanto tempo uma habilidade disponível mostra PRONTO antes de desaparecer. 0 remove assim que fica pronta."),
    "ui.tracking": ("Suivi", "Tracking",
        "Rastreamento"),
    "ui.track_summoners": ("Sorts d'invocateur (exact)",
                           "Summoner spells (exact)",
        "Feitiços de invocador (exatos)"),
    "ui.track_ultimates": ("Ultimes (approximatif, ~)",
                           "Ultimates (approximate, ~)",
        "Ultimates (estimadas, ~)"),
    "ui.chat_calls": ("Timers annonces dans le chat",
                      "Timers called in chat",
        "Tempos informados no chat"),
    "ui.chat_calls_tip": (
        "Un coequipier qui tape \"jgl flash 950\" lance le timer du jungler "
        "jusqu'a 9:50 sur l'horloge de la partie. Le role (top, jgl, mid, adc, "
        "supp) ou le nom du champion, le sort, et l'heure : les trois sont "
        "obligatoires. Sans heure, rien ne demarre -- \"top no flash\" n'est pas "
        "un timer. Ces timers portent le \"?\", parce qu'ils viennent de "
        "quelqu'un et pas du jeu.",
        "A teammate typing \"jgl flash 950\" starts the jungler's timer until "
        "9:50 on the game clock. The role (top, jgl, mid, adc, supp) or the "
        "champion's name, the spell, and the time: all three are required. With "
        "no time nothing starts -- \"top no flash\" is not a timer. These timers "
        "carry the \"?\", because they come from somebody rather than from the "
        "game.",
        "Um aliado digitando \"jg flash 950\" inicia o temporizador da selva até 9:50 no relógio da partida. É preciso informar função ou campeão, feitiço e horário. Sem horário, nada começa: \"top sem flash\" não é um temporizador. Esses tempos recebem \"?\", pois vêm de uma pessoa."),
    "ui.auto_roles": ("Lire les roles ennemis a l'ecran",
                      "Read the enemy roles from the screen",
        "Ler funções inimigas na tela"),
    "ui.auto_roles_tip": (
        "L'ecran de chargement et le scoreboard listent une equipe dans l'ordre "
        "des lignes : top, jungle, mid, adc, support. Les deux zones se cadrent "
        "dans Depannage. Decochez pour ne garder que les roles choisis a la main "
        "dans la liste des ennemis.",
        "The loading screen and the scoreboard both list a team in lane order: "
        "top, jungle, mid, adc, support. Both areas are framed on the "
        "Troubleshooting page. Untick to keep only the roles picked by hand in "
        "the enemies list.",
        "A tela de carregamento e o placar listam a equipe na ordem: topo, selva, meio, atirador e suporte. Enquadre as duas áreas em Ajuda. Desmarque para usar apenas as funções escolhidas na lista de inimigos."),
    "ui.enemy_colour": ("Uniquement les ennemis", "Enemies only",
        "Somente inimigos"),
    "ui.enemy_colour_tip": (
        "Ne concerne que les lignes du type \"Attendez <champion> <sort> - N "
        "sec.\", qui indiquent un temps restant sans dire de quelle equipe il "
        "s'agit : seule la couleur du nom le dit. Laissez decoche si vous tapez "
        "cette phrase vous-meme pour tester l'OCR, car votre propre texte n'est "
        "pas affiche en rouge. Les annonces \"a utilise\" ne sont jamais "
        "filtrees : le jeu ne les affiche que pour les ennemis.",
        "Only affects lines like \"Wait <champion> <spell> - N sec.\", which "
        "state a remaining time without saying whose it is: only the colour of "
        "the name does. Leave it unticked if you type that line yourself to test "
        "the OCR, since your own text is not drawn in red. \"used\" "
        "announcements are never filtered: the game prints those for enemies "
        "only.",
        "Afeta apenas linhas com segundos restantes, como a hipótese \"Aguarde <campeão> <feitiço> - N seg.\": a cor do nome identifica o inimigo. Deixe desmarcado ao digitar uma linha de teste, pois seu texto não aparece em vermelho. Anúncios com \"usou\" não passam por esse filtro."),
    "ui.cosmic": ("Supposer Perspicacite cosmique (-18%)",
                  "Assume Cosmic Insight (-18%)",
        "Considerar Perspicácia Cósmica (-18%)"),
    "ui.ionian": ("Supposer Bottes ioniennes (-12%)",
                  "Assume Ionian Boots of Lucidity (-12%)",
        "Considerar Botas Ionianas da Lucidez (-12%)"),
    "ui.ultimate_note": (
        "Les ultimes dependent du rang et de l'acceleration de competences, "
        "invisibles a l'ecran. Ils sont estimes d'apres l'horloge de la partie "
        "et marques d'un ~.",
        "Ultimates depend on ability rank and haste, neither of which is visible "
        "on screen. They are estimated from the game clock and marked with a ~.",
        "Ultimates variam com nível e aceleração. O tempo é estimado pelo relógio da partida e recebe ~."),
    "ui.notifications": ("Notifications", "Notifications",
        "Notificações"),
    "ui.audio": ("Activer le son", "Enable sound",
        "Ativar som"),
    "ui.audio_ready": ("Signaler les sorts prets", "Announce ready spells",
        "Avisar quando habilidades voltarem"),
    "ui.audio_warn": ("Alerte avant :", "Warn before:",
        "Avisar com antecedência de:"),
    "ui.audio_sfx": ("Son :", "Sound:",
        "Som:"),
    "ui.audio_preview": ("Ecouter", "Play",
        "Ouvir"),
    "ui.audio_preview_tip": (
        "Joue le son de retour de sort. Choisir dans la liste le joue aussi, "
        "meme si les notifications sont coupees.",
        "Plays the spell-is-back cue. Picking from the list plays it too, even "
        "when notifications are switched off.",
        "Reproduz o aviso de habilidade disponível. Selecionar um som na lista também o reproduz, mesmo com as notificações desligadas."),

    # -- the notification voices -----------------------------------------
    # Named for what they sound like rather than for how they are made: nobody
    # picks a cue by its synthesis engine. Listed in the order the settings show
    # them, which walks through the families -- struck, metallic, breathy,
    # sliding, wavering, swelling -- instead of shuffling them.
    "sfx.chime": ("Carillon", "Chime",
        "Sino suave"),
    "sfx.bell": ("Cloche", "Bell",
        "Sino"),
    "sfx.bowl": ("Bol chantant", "Singing bowl",
        "Tigela tibetana"),
    "sfx.marimba": ("Marimba", "Marimba",
        "Marimba"),
    "sfx.harp": ("Harpe", "Harp",
        "Harpa"),
    "sfx.musicbox": ("Boite a musique", "Music box",
        "Caixa de música"),
    "sfx.knock": ("Toc-toc", "Knock",
        "Batida"),
    "sfx.tick": ("Tic", "Tick",
        "Tique"),
    "sfx.fmbell": ("Cloche metallique", "Metal bell",
        "Sino metálico"),
    "sfx.glass": ("Verre", "Glass",
        "Vidro"),
    "sfx.reed": ("Anche", "Reed",
        "Palheta"),
    "sfx.clave": ("Claves", "Claves",
        "Claves"),
    "sfx.breath": ("Souffle", "Breath",
        "Sopro"),
    "sfx.brush": ("Balai", "Brush",
        "Escova"),
    "sfx.shaker": ("Maracas", "Shaker",
        "Chocalho"),
    "sfx.hush": ("Chuchotement", "Hush",
        "Sussurro"),
    "sfx.swoop": ("Montee", "Swoop",
        "Deslize"),
    "sfx.droplet": ("Goutte", "Droplet",
        "Gota"),
    "sfx.warble": ("Tremolo", "Warble",
        "Trinado"),
    "sfx.vibrato": ("Vibrato", "Vibrato",
        "Vibrato"),
    "sfx.pad": ("Nappe", "Pad",
        "Som ambiente"),
    "sfx.choir": ("Choeur", "Choir",
        "Coro"),
    "ui.capture": ("Capture", "Capture",
        "Captura"),
    "ui.interval": ("Intervalle :", "Interval:",
        "Intervalo:"),

    "ui.startup": ("Demarrage", "Startup",
        "Inicialização"),
    "ui.autostart": ("Lancer au demarrage de Windows", "Start with Windows",
        "Iniciar com o Windows"),
    "ui.autostart_note": (
        "Le programme doit tourner avant le debut de la partie : il ne peut "
        "pas rattraper les annonces ecrites avant son lancement. Windows laisse aussi "
        "desactiver cette entree dans le Gestionnaire des taches, onglet "
        "Demarrage.",
        "The program has to be running before the game starts: it cannot "
        "recover announcements printed before it launched. Windows also lets you switch this "
        "entry off from Task Manager's Startup tab.",
        "O programa precisa estar aberto antes da partida: ele não recupera anúncios anteriores à sua abertura. Você também pode desativá-lo na aba Inicializar do Gerenciador de Tarefas."),
    "ui.open_window_note": (
        "La fenetre s'ouvre toujours au lancement, meme avec Windows. Fermer "
        "avec X la masque dans la zone de notification. Double-cliquez sur "
        "l'icone pour la rouvrir.",
        "The window always opens on launch, including with Windows. Closing "
        "with X hides it in the notification area. Double-click the tray icon "
        "to reopen it.",
        "A janela sempre aparece ao iniciar, inclusive com o Windows. Fechar no X envia para a bandeja. Clique duas vezes no ícone para reabrir."),
    "ui.autostart_failed": (
        "Windows a refuse la modification (strategie de securite ?). "
        "L'entree de demarrage n'a pas ete changee.",
        "Windows refused the change (security policy?). The startup entry was "
        "not modified.",
        "O Windows recusou a alteração (política de segurança?). A entrada de inicialização não foi modificada."),

    "ui.updates": ("Mises a jour", "Updates",
        "Atualizações"),
    "ui.update_check": ("Verifier et telecharger au demarrage", "Check and download on start-up",
        "Verificar e baixar ao iniciar"),
    "ui.update_check_tip": (
        "Consulte GitHub au lancement et telecharge une version plus recente en arriere-plan. Elle est appliquee a la fermeture, ou avec Mettre a jour maintenant.",
        "Checks GitHub at launch and downloads a newer version in the background. Applied when you quit, or with Update now.",
        "Consulta o GitHub ao abrir e baixa uma versão mais recente em segundo plano. Aplica ao sair do programa ou pelo botão Atualizar agora."),
    "ui.update_installed": ("Version installee :", "Installed version:",
        "Versão instalada:"),
    "ui.update_check_now": ("Verifier maintenant", "Check now",
        "Verificar agora"),
    "ui.update_checking": ("Verification...", "Checking...",
        "Verificando..."),
    "ui.update_up_to_date": ("Vous avez la derniere version.",
                             "You have the latest version.",
        "Você está usando a versão mais recente."),
    "ui.update_unavailable": (
        "Verification impossible (pas de reseau ?).",
        "Could not check (no network?).",
        "Não foi possível verificar (sem conexão?)."),
    "ui.update_from_source": (
        "Lance depuis les sources : il n'y a pas d'executable a remplacer.",
        "Running from source: there is no executable to replace.",
        "Executando pelo código-fonte: não há executável para substituir."),

    # -- enemies and their roles -----------------------------------------
    "ui.team_help": (
        "Les champions apparaissent des que l'ecran de chargement ou le "
        "scoreboard est lu, ou au premier sort detecte. Le role choisi ici "
        "l'emporte toujours sur celui lu a l'ecran.",
        "Champions appear as soon as the loading screen or the scoreboard is "
        "read, or on the first spell detected. A role picked here always wins "
        "over one read off the screen.",
        "Os campeões aparecem após a leitura da tela ou da primeira habilidade."),
    "ui.team_empty": (
        "Aucun ennemi repere pour l'instant. Ils s'ajoutent tout seuls au premier "
        "sort detecte.",
        "No enemy spotted yet. They add themselves on the first spell detected.",
        "Nenhum inimigo identificado ainda."),

    # -- troubleshooting page --------------------------------------------
    "ui.help_intro": (
        "Si aucun timer n'apparait, la cause est presque toujours l'une des "
        "trois : League n'est pas en fenetre sans bordure, la langue ne "
        "correspond pas a celle du client, ou la zone du chat est mal cadree.",
        "If no timer appears, it is nearly always one of three things: League is "
        "not in borderless windowed mode, the language does not match the "
        "client's, or the chat area is framed wrong.",
        "Se nenhum temporizador aparece, quase sempre é uma destas três coisas: League fora do modo sem bordas, idioma diferente do cliente ou área do chat enquadrada incorretamente."),
    "ui.chat_area": ("Zone du chat", "Chat area",
        "Área do chat"),
    "ui.chat_area_hint": (
        "Trouvee automatiquement d'apres le contenu du chat. Ces boutons servent "
        "quand elle ne l'est pas.",
        "Found automatically from what the chat contains. These buttons are for "
        "when it is not.",
        "Localizada automaticamente pelo conteúdo do chat. Use estes botões quando isso falhar."),
    "ui.zones": ("Cadrer les zones lues", "Frame the areas being read",
        "Enquadrar áreas de leitura"),
    "ui.zones_hint": (
        "Chaque bouton pose un cadre a l'ecran, que vous deplacez pendant la "
        "partie ; il affiche en direct ce que l'OCR lit dedans.",
        "Each button puts a frame on screen that you move during a game; it "
        "reports live what the OCR reads inside it.",
        "Cada botão mostra uma moldura para posicionar durante a partida, com o texto que o OCR está lendo dentro dela."),
    "ui.diagnostics": ("Ce que l'application lit", "What the application reads",
        "O que o programa está lendo"),

    # -- debug readouts --------------------------------------------------
    "ui.debug_lines": ("Lignes lues par l'OCR :", "Lines read by the OCR:",
        "Linhas lidas pelo OCR:"),
    "ui.debug_misses": (
        "Lignes contenant un champion mais non interpretees. Si le jeu annonce "
        "les sorts avec une formulation differente, elle apparait ici :",
        "Lines naming a champion that were not understood. If the game words "
        "spell announcements differently, it shows up here:",
        "Linhas que citam um campeão, mas não foram entendidas. Se o jogo usar outro formato nos anúncios de habilidades, ele aparecerá aqui:"),
    "ui.debug_colour": (
        "Sorts lus mais ignores car le champion n'etait pas affiche en rouge, "
        "donc pas un ennemi (ping sur son propre sort, sort d'un allie) :",
        "Spells read but ignored because the champion was not drawn in red, so "
        "not an enemy (a ping on one's own spell, an ally's spell):",
        "Habilidades lidas, mas ignoradas porque o nome não estava em vermelho (ping de habilidade própria ou de aliado):"),
    "ui.debug_events": ("Evenements confirmes :", "Confirmed events:",
        "Eventos reconhecidos:"),

    # -- the setup guide -------------------------------------------------
    # Seven screens, drawn from design/maquette/Onboarding *.dc.html. The wording
    # is the mockups' own, which means two things this catalogue does nowhere
    # else: it says "tu", and it is written with its accents. The rest of the
    # file is ASCII because it was written before anything drew accented text;
    # the guide draws every word of itself with an embedded font that has them.
    "guide.title": ("Guide d'installation", "Setup guide",
        "Guia de configuração"),
    "guide.step": ("Etape {step} sur {total}", "Step {step} of {total}",
        "Etapa {step} de {total}"),
    "guide.back": ("Retour", "Back",
        "Voltar"),
    "guide.next": ("Suivant", "Next",
        "Avançar"),
    "guide.finish": ("Terminer", "Finish",
        "Concluir"),

    # The eight labels under the stepper's circles.
    "guide.nav_language": ("Langue du client", "Client language",
        "Idioma do cliente"),
    "guide.nav_welcome": ("Bienvenue", "Welcome",
        "Boas-vindas"),
    "guide.nav_borderless": ("Fenêtré sans bordure", "Borderless window",
        "Janela sem bordas"),
    "guide.nav_layout": ("Choisir l'affichage", "Pick a display",
        "Escolher exibição"),
    "guide.nav_tune": ("Le régler", "Tune it",
        "Ajustar"),
    "guide.nav_place": ("Le poser", "Place it",
        "Posicionar"),
    "guide.nav_proof": ("La preuve", "The proof",
        "Teste"),
    "guide.nav_done": ("Tout est prêt", "All set",
        "Tudo pronto"),

    # -- 1. the client's language ----------------------------------------
    "guide.language_title": ("Langue du client", "Client language",
        "Idioma do cliente"),
    "guide.language_lead": (
        "Le Guide et l'overlay parlent <b>la même langue</b> que ton client "
        "League of Legends.",
        "The guide and the overlay speak <b>the same language</b> as your "
        "League of Legends client.",
        "O guia e o overlay usam <b>o mesmo idioma</b> do seu cliente League of Legends."),
    "guide.language_lead_2": (
        "Sélectionne celle de ton client juste en dessous.",
        "Pick your client's language just below.",
        "Escolha o idioma do seu cliente ao lado."),
    "guide.language_note": (
        "Tu pourras la changer plus tard dans les paramètres du Guide.",
        "You can change it later in the guide's settings.",
        "Você pode alterar o idioma depois nas configurações."),
    "guide.language_pick": (
        "Sélectionne la langue de ton client League of Legends",
        "Pick your League of Legends client language",
        "Escolha o idioma do seu cliente League of Legends"),
    # A language's own name, which does not change with the interface language.
    "guide.language_fr_name": ("Français", "Français",
        "Français"),
    "guide.language_en_name": ("English", "English",
        "English"),
    "guide.language_fr_sub": ("Version française", "French version",
        "Versão francesa"),
    "guide.language_en_sub": ("English version", "English version",
        "Versão em inglês"),

    # -- 2. welcome ------------------------------------------------------
    "guide.welcome_title": ("Bienvenue", "Welcome",
        "Boas-vindas"),
    "guide.welcome_lead": (
        "Nous allons tout configurer dans <b>l'Outil d'entraînement.</b>",
        "We are going to set everything up in the <b>Practice Tool.</b>",
        "Vamos configurar tudo na <b>Ferramenta de Treino.</b>"),
    "guide.welcome_path": (
        "Ouvre League of Legends, puis suis ce chemin dans le client :",
        "Open League of Legends, then follow this path in the client:",
        "Abra League of Legends e siga este caminho no cliente:"),
    "guide.welcome_blurb": (
        "Apprends à maîtriser ton champion favori grâce à cet "
        "entraînement de 1 à 10 joueurs dans la Faille de l'invocateur !",
        "Learn to master your favourite champion in this 1-to-10 player "
        "practice game on Summoner's Rift!",
        "Pratique com seu campeão favorito em uma partida de treino em Summoner's Rift!"),
    "guide.welcome_path_play": ("JOUER", "PLAY",
        "JOGAR"),
    "guide.welcome_path_training": ("ENTRAÎNEMENT", "TRAINING",
        "TREINAMENTO"),
    "guide.welcome_path_tool": ("OUTIL D'ENTRAÎNEMENT", "PRACTICE TOOL",
        "FERRAMENTA DE TREINO"),
    "guide.welcome_note": (
        "C'est un environnement d'entraînement privé : personne ne t'y attend, "
        "prends ton temps.",
        "It is a private practice environment: nobody is waiting for you, take "
        "your time.",
        "É um ambiente de treino privado: ninguém está esperando por você, pode ir com calma."),

    # -- 3. borderless ---------------------------------------------------
    "guide.borderless_step_1": ("Va dans l'onglet <b>VIDÉO</b>.",
                                "Go to the <b>VIDEO</b> tab.",
        "Abra a aba <b>VÍDEO</b>."),
    "guide.borderless_step_2": (
        "Dans <b>Mode fenêtré</b>, sélectionne <b>Sans bord</b>.",
        "Under <b>Window mode</b>, select <b>Borderless</b>.",
        "Em <b>Modo de janela</b>, selecione <b>Sem bordas</b>."),
    "guide.borderless_avoid": ("À éviter : Plein écran", "Avoid: Fullscreen",
        "Evite: Tela cheia"),
    "guide.borderless_avoid_body": (
        "Le mode plein écran peut cacher l'overlay et empêcher le Guide de "
        "fonctionner.",
        "Fullscreen can hide the overlay and stop the guide from working.",
        "A tela cheia pode ocultar o overlay e impedir o funcionamento do guia."),
    "guide.borderless_note": (
        "Le mode Sans bord permet d'afficher correctement l'overlay tout en "
        "restant dans le jeu.",
        "Borderless lets the overlay draw properly while you stay in the game.",
        "O modo sem bordas permite que o overlay apareça corretamente durante a partida."),

    # -- 4. pick a display -----------------------------------------------
    "guide.layout_title": ("Choisir l'affichage", "Pick a display",
        "Escolher exibição"),
    "guide.layout_lead": (
        "Clique sur un affichage à gauche. <b>Le résultat s'affiche en direct à "
        "droite</b> dans le Practice Tool.",
        "Click a display on the left. <b>The result shows live on the right</b> "
        "in the Practice Tool.",
        "Escolha uma exibição à esquerda. <b>O resultado aparece à direita</b> na Ferramenta de Treino."),
    "guide.layout_note": (
        "Tu pourras changer d'affichage plus tard dans les paramètres.",
        "You can change the display later in the settings.",
        "Você pode mudar a exibição depois nas configurações."),
    "guide.layout_result": ("Résultat dans le Practice Tool",
                            "The result in the Practice Tool",
        "Resultado na Ferramenta de Treino"),
    "guide.layout_recommended": ("Recommandé", "Recommended",
        "Recomendado"),

    # -- 5. tune it ------------------------------------------------------
    "guide.tune_title": ("Le régler", "Tune it",
        "Ajustar"),
    "guide.tune_lead": (
        "Chaque réglage change <b>l'aperçu à droite</b> pendant que tu le "
        "tournes.",
        "Every setting changes <b>the preview on the right</b> as you turn "
        "it.",
        "Cada ajuste muda <b>a prévia à direita</b> na hora."),
    "guide.tune_behaviour": ("Ce qu'il affiche", "What it shows",
        "O que mostrar"),
    "guide.tune_note": (
        "Le chrono est le seul texte dont tu choisis la police : les noms "
        "gardent celle du programme.",
        "The countdown is the only text whose face you pick: the names keep "
        "the program's own.",
        "A fonte escolhida afeta apenas a contagem. Os nomes mantêm a fonte do programa."),
    "guide.tune_reset": ("Tout remettre par défaut", "Put it all back",
        "Restaurar ajustes"),
    "guide.tune_reset_ask": ("Remettre ces réglages par défaut ?",
                             "Reset these settings to their defaults?",
        "Restaurar os valores padrão destes ajustes?"),
    "guide.tune_reset_yes": ("Oui, remettre", "Yes, reset",
        "Sim, restaurar"),
    "guide.tune_reset_no": ("Annuler", "Cancel",
        "Cancelar"),

    # -- 6. place it -----------------------------------------------------
    "guide.place_title": ("Le poser", "Place it",
        "Posicionar"),
    "guide.place_lead": (
        "L'affichage se glisse <b>n'importe où à l'écran</b>. Déverrouille-le, "
        "attrape-le, pose-le où tu veux le lire pendant une partie.",
        "The display drags <b>anywhere on screen</b>. Unlock it, grab it, drop "
        "it wherever you want to read it during a game.",
        "Arraste a exibição para <b>qualquer lugar da tela</b>. Destrave e posicione onde você quer acompanhar os tempos durante a partida."),
    "guide.place_action": ("Le placer maintenant", "Place it now",
        "Posicionar agora"),
    "guide.place_note": (
        "En partie, la barre garde les vrais timers et se verrouille à la fin du "
        "guide. Hors partie, des exemples s'affichent. Glisse et redimensionne "
        "par le coin en bas à droite.",
        "During a game, the bar keeps your real timers and locks when you finish "
        "the guide. Outside a game, samples appear. Drag and resize from the "
        "bottom-right corner.",
        "Em partida, a barra mantém seus timers reais e trava ao concluir o guia. Fora de partida, aparecem exemplos. Arraste e redimensione pelo canto inferior direito."),
    "guide.place_anywhere": ("ou n'importe où ailleurs", "or anywhere else",
        "ou em qualquer outro lugar"),

    # -- 7. the proof ----------------------------------------------------
    "guide.proof_title": ("La preuve", "The proof",
        "Teste"),
    "guide.proof_lead": (
        "Une vraie image de partie est fournie avec le programme. "
        "<b>Un timer apparaît</b> : la chaîne entière fonctionne.",
        "A real game frame ships with the program. <b>A timer appears</b>: "
        "the whole chain works.",
        "O programa inclui uma captura inglesa real. <b>Um temporizador aparece</b> quando a cadeia de leitura funciona. O teste não valida o cliente brasileiro."),
    "guide.proof_action": ("Lancer le test", "Run the test",
        "Executar teste"),
    "guide.proof_running": ("Lecture...", "Reading...",
        "Lendo..."),
    # Says only what is true on a second press too, when the timers it would have
    # started are already running. The countdown beside each spell is what reports
    # a timer that did start.
    "guide.proof_pass": ("{count} sorts lus sur l'image.",
                         "{count} spells read from the frame.",
        "{count} habilidades lidas na captura."),
    "guide.proof_note": (
        "Rien n'est injecté dans League, sa mémoire n'est jamais lue, aucun clic "
        "ni appui de touche n'est envoyé au jeu. Uniquement les pixels déjà "
        "affichés sur ton écran.",
        "Nothing is injected into League, its memory is never read, and no click "
        "or key press is ever sent to the game. Only the pixels already on your "
        "screen.",
        "Nada é injetado no League, sua memória nunca é lida e nenhum clique ou tecla é enviado ao jogo. Apenas os pixels já visíveis na sua tela."),
    "guide.proof_read": ("lue", "read",
        "lida"),
    "guide.proof_frame": (
        "Rien n'apparaît ? La zone du chat est trouvée toute seule ; si elle "
        "tombe à côté, ce bouton affiche un cadre à poser sur le tien, et "
        "montre en direct ce qui est lu dessous. Il reste dans Dépannage.",
        "Nothing appeared? The chat area is found on its own; if it lands in "
        "the wrong place, this button draws a box to put over yours, and shows "
        "live what it reads underneath. It stays in Troubleshooting.",
        "Nada apareceu? A área do chat é localizada automaticamente. Se estiver fora do lugar, este botão mostra uma moldura para posicionar sobre seu chat e exibe o que está sendo lido. Ele continua disponível em Ajuda."),

    # -- 8. all set ------------------------------------------------------
    "guide.done_title": ("Tout est prêt !", "All set!",
        "Tudo pronto!"),
    "guide.done_lead": (
        "Ton client League of Legends est maintenant configuré et optimisé.",
        "Your League of Legends client is now set up and ready.",
        "A configuração do Flashwatch está pronta."),
    "guide.done_check_display": ("Affichage optimisé", "Display set up",
        "Exibição configurada"),
    "guide.done_check_borderless": ("Fenêtré sans bordure", "Borderless window",
        "Janela sem bordas"),
    "guide.done_check_settings": ("Paramètres appliqués", "Settings applied",
        "Ajustes aplicados"),
    "guide.done_footer": (
        "Tu peux modifier ces paramètres à tout moment dans les <b>options.</b>",
        "You can change these settings at any time in the <b>options.</b>",
        "Você pode alterar esses ajustes quando quiser nas <b>opções.</b>"),

    # Words drawn inside the illustrations. Two of the figures redraw League's
    # own client, so those are the client's labels rather than ours -- which is
    # the point: they are what has to be found on a screen this program never
    # sees.
    "guide.shot_chat": ("le chat de la partie", "the game chat",
        "chat da partida"),
    "guide.shot_bar": ("les timers", "the timers",
        "temporizadores"),
    "guide.shot_options": ("OPTIONS", "OPTIONS",
        "OPÇÕES"),
    "guide.shot_tab_hotkeys": ("RACCOURCIS", "HOTKEYS",
        "ATALHOS"),
    "guide.shot_tab_camera": ("CAMÉRA", "CAMERA",
        "CÂMERA"),
    "guide.shot_tab_video": ("VIDÉO", "VIDEO",
        "VÍDEO"),
    "guide.shot_tab_audio": ("AUDIO", "AUDIO",
        "ÁUDIO"),
    "guide.shot_tab_interface": ("INTERFACE", "INTERFACE",
        "INTERFACE"),
    "guide.shot_tab_game": ("JEU", "GAME",
        "JOGO"),
    "guide.shot_general": ("Général", "General",
        "Geral"),
    "guide.shot_resolution": ("Résolution", "Resolution",
        "Resolução"),
    "guide.shot_mode": ("Mode fenêtré", "Window mode",
        "Modo de janela"),
    "guide.shot_borderless": ("Sans bord", "Borderless",
        "Sem bordas"),
    "guide.shot_fullscreen": ("Plein écran", "Fullscreen",
        "Tela cheia"),
    "guide.shot_graphics": ("Graphismes", "Graphics",
        "Gráficos"),
    "guide.shot_quality": ("Très élevé", "Very high",
        "Muito alta"),
    "guide.shot_save": ("Sauvegarder", "Save",
        "Salvar"),
    "guide.shot_cancel": ("Annuler", "Cancel",
        "Cancelar"),
    "guide.shot_play": ("JOUER", "PLAY",
        "JOGAR"),
    "guide.shot_training": ("ENTRAÎNEMENT", "TRAINING",
        "TREINAMENTO"),
    "guide.shot_tutorial": ("DIDACTICIEL", "TUTORIAL",
        "TUTORIAL"),
    "guide.shot_practice": ("OUTIL D'ENTRAÎNEMENT", "PRACTICE TOOL",
        "FERRAMENTA DE TREINO"),
    "guide.shot_confirm": ("CONFIRMER", "CONFIRM",
        "CONFIRMAR"),

    # -- region picker ---------------------------------------------------
    "picker.hint": ("Tracez un rectangle autour du chat  -  Echap pour annuler",
                    "Draw a rectangle around the chat  -  Esc to cancel",
        "Desenhe um retângulo ao redor do chat - Esc para cancelar"),

    # -- test-mode frame -------------------------------------------------
    "zone.title": ("Zone OCR (mode test)", "OCR zone (test mode)",
        "Área de OCR (modo de teste)"),
    "zone.name_chat": ("CHAT", "CHAT",
        "CHAT"),
    "zone.name_clock": ("TEMPS DE PARTIE", "GAME CLOCK",
        "RELÓGIO DA PARTIDA"),
    "zone.name_scoreboard": ("SCOREBOARD (ENNEMIS)", "SCOREBOARD (ENEMIES)",
        "PLACAR (INIMIGOS)"),
    "zone.name_loading": ("ECRAN DE CHARGEMENT", "LOADING SCREEN",
        "TELA DE CARREGAMENTO"),
    "zone.clock_read": ("horloge lue : {value}", "clock read: {value}",
        "horário lido: {value}"),
    "zone.clock_unreadable": ("aucune horloge lisible dans ce cadre",
                              "no readable clock inside this frame",
        "nenhum horário legível nesta moldura"),
    "zone.clock_hint": ("Cadrez le chronometre en haut de l'ecran (mm:ss).",
                        "Frame the match timer at the top of the screen (mm:ss).",
        "Enquadre o relógio da partida no alto da tela (mm:ss)."),
    "zone.scoreboard_hint": (
        "Maintenez Tab, puis cadrez la colonne des cinq portraits ennemis "
        "(haut en bas : top, jungle, mid, adc, support).",
        "Hold Tab, then frame the column of five enemy portraits (top to "
        "bottom: top, jungle, mid, adc, support).",
        "Segure Tab e enquadre a coluna dos cinco retratos inimigos (de cima para baixo: topo, selva, meio, atirador e suporte)."),
    "zone.loading_hint": (
        "Cadrez la rangee des cinq ennemis sur l'ecran de chargement "
        "(gauche a droite : top, jungle, mid, adc, support).",
        "Frame the row of five enemies on the loading screen (left to right: "
        "top, jungle, mid, adc, support).",
        "Enquadre os cinco inimigos na tela de carregamento (da esquerda para a direita: topo, selva, meio, atirador e suporte)."),
    "zone.roles_read": ("roles reconnus : {roles}", "roles recognised: {roles}",
        "funções reconhecidas: {roles}"),
    "zone.roles_none": ("aucun champion reconnu dans ce cadre",
                        "no champion recognised inside this frame",
        "nenhum campeão reconhecido nesta moldura"),
    "zone.searching": ("recherche", "searching",
        "buscando"),
    "zone.fixed": ("zone fixee", "area pinned",
        "área fixada"),
    "zone.header": ("MODE TEST  -  {width}x{height} @ {x},{y}  ({state})",
                    "TEST MODE  -  {width}x{height} @ {x},{y}  ({state})",
        "MODO DE TESTE - {width}x{height} @ {x},{y} ({state})"),
    "zone.rows": ("{rows} ligne(s) lue(s), {chat} reconnue(s) comme chat",
                  "{rows} line(s) read, {chat} recognised as chat",
        "{rows} linha(s) lida(s), {chat} reconhecida(s) como chat"),
    "zone.last_chat": ("derniere ligne chat : {line}", "last chat line: {line}",
        "última linha do chat: {line}"),
    "zone.no_chat": ("aucune ligne de chat lue pour l'instant",
                     "no chat line read yet",
        "nenhuma linha do chat lida ainda"),
    "zone.keys": (
        "Bords = deplacer/redimensionner  -  fleches = 1 px  -  "
        "Maj+fleches = 10 px  -  Ctrl+fleches = taille",
        "Edges = move/resize  -  arrows = 1 px  -  Shift+arrows = 10 px  -  "
        "Ctrl+arrows = size",
        "Bordas = mover/redimensionar - setas = 1 px - Shift+setas = 10 px - Ctrl+setas = tamanho"),
    "zone.apply": ("Valider", "Apply",
        "Aplicar"),
    "zone.cancel": ("Annuler", "Cancel",
        "Cancelar"),
    "ui.language_pt": ("Português (Brasil)", "Português (Brasil)", "Português (Brasil)"),
    "guide.language_pt_name": ("Português", "Português", "Português"),
    "guide.language_pt_sub": ("Brasil", "Brasil", "Brasil"),
    "overlay.ready": ("READY", "READY", "PRONTO"),
    "role.top": ("TOP", "TOP", "TOPO"),
    "role.jungle": ("JUNGLE", "JUNGLE", "SELVA"),
    "role.mid": ("MID", "MID", "MEIO"),
    "role.adc": ("ADC", "ADC", "ADC"),
    "role.support": ("SUPPORT", "SUPPORT", "SUPORTE"),
    "spell.ultimate": ("Ultime", "Ultimate", "Ultimate"),
    "update.cancelled": ("annule", "cancelled", "cancelado"),
    "update.bad_size": ("{expected} octets attendus, {actual} recus", "expected {expected} bytes, got {actual}", "Esperados {expected} bytes, recebidos {actual}"),
    "update.too_small": ("seulement {size} octets, pas un executable", "only {size} bytes, not an executable", "Apenas {size} bytes; não é um executável"),
    "update.not_executable": ("le fichier telecharge n'est pas un programme Windows", "the downloaded file is not a Windows program", "O arquivo baixado não é um programa do Windows"),
    "update.missing_file": ("{name} est absent", "{name} is missing", "O arquivo {name} não foi encontrado"),
    "update.too_many_backups": ("trop de copies de la version precedente", "too many leftover copies of the previous version", "Há cópias demais da versão anterior"),
    "update.move_failed": ("impossible de deplacer la version actuelle ({error})", "could not move the current version aside ({error})", "Não foi possível mover a versão atual ({error})"),
    "update.restore_manually": ("la mise a jour a echoue ; renommez {backup} en {target}", "the update failed and the old version is now named {backup}; rename it back to {target}", "A atualização falhou e a versão anterior agora se chama {backup}; renomeie para {target}"),
    "update.replace_failed": ("impossible d'installer la nouvelle version ({error})", "could not put the new version in place ({error})", "Não foi possível instalar a nova versão ({error})"),
    "test.unreadable_image": ("{path} : image illisible", "{path}: unreadable image", "{path}: imagem ilegível"),
}
