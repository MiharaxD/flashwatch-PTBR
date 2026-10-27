"""Brazilian localization contracts. Fixtures are Riot JSON, not client captures.

Only the `usou` cast wording has official Riot textual evidence. Every wait
example below is explicitly a hypothesis; OCR glyph mutations are synthetic.
"""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import _bootstrap  # noqa: F401
from pathlib import Path
import re
import string
import tempfile
import time
import unittest

import i18n
from cooldowns import COOLDOWNS, normalise_spell
from message_parser import MessageParser, looks_like_chat_line
from ptbr_assets import FIXTURE, load_assets
from roles import role_from_word
from settings import Settings
from timer_manager import ActiveTimer, TimerManager


class BrazilianTests(unittest.TestCase):
    def setUp(self):
        self.assets, self.requests = load_assets()
        self.parser = MessageParser(self.assets)
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "settings.json")
        self.settings.set("locale", "pt_BR", save=False)
        i18n.set_language("pt_BR")

    def tearDown(self):
        i18n.set_language(i18n.ENGLISH)
        self.temp.cleanup()

    def test_catalog_and_formatting(self):
        formatter = string.Formatter()
        for key, values in i18n.STRINGS.items():
            with self.subTest(key=key):
                self.assertEqual(len(values), len(i18n.LANGUAGES))
                self.assertTrue(all(value.strip() for value in values))
                fields = [{(field, spec, conversion) for _, field, spec, conversion
                           in formatter.parse(value) if field is not None} for value in values]
                self.assertEqual(fields[0], fields[2])
                self.assertEqual(re.findall(r"</?b>", values[1]), re.findall(r"</?b>", values[2]))
        self.assertEqual(i18n.tr("game.in_game", width=1920, height=1080), "Em partida (1920x1080)")

    def test_locale_and_official_loader(self):
        for value in ("pt", "pt_BR", "pt-BR", "PT_br"):
            self.assertEqual(i18n.set_language(value), i18n.PORTUGUESE)
        self.assertEqual(i18n.locale_for(i18n.PORTUGUESE), "pt_BR")
        self.assertEqual(i18n.language_for("pt_PT"), i18n.ENGLISH)
        self.assertEqual(i18n.language_for("de_DE"), i18n.ENGLISH)
        self.assertEqual(set(self.assets.champions), set(FIXTURE["champions"]["data"]))
        for cache, url in self.requests:
            self.assertIn(f"-{self.assets.version}-pt_BR.json", cache)
            self.assertIn(f"/{self.assets.version}/data/pt_BR/", url)
        for cid, champion in self.assets.champions.items():
            self.assertEqual(champion.champion_id, cid)
            self.assertEqual(champion.ultimate.name, FIXTURE["champions"]["data"][cid]["spells"][3]["name"])
        self.assertEqual(self.assets.champions["MonkeyKing"].name, "Wukong")

    def test_official_cast_wording(self):
        # Riot's patch 25.17 notes explicitly quote these two lines.
        for text, cid in (("Diana usou Flash", "Diana"), ("Jinx usou Flash", "Jinx")):
            for prefix in ("", "(14:23) ", "14:23 Jogador (Lux): "):
                event = self.parser.parse_line(prefix + text)
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.spell_key, event.certain), (cid, "Flash", True))

    def test_all_official_spell_and_ultimate_names(self):
        # Synthetic sentences derived from the evidenced template + Riot names.
        for key, spell in self.assets.spells.items():
            with self.subTest(spell=key):
                event = self.parser.parse_line(f"12:04 Jogador (Lux): Ahri usou {spell.name}")
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.spell_key), ("Ahri", key))
                self.assertEqual(event.spell_name, spell.name)
        for cid, champion in self.assets.champions.items():
            with self.subTest(champion=cid, ultimate=champion.ultimate.name):
                event = self.parser.parse_line(f"12:04 Jogador (Lux): {champion.name} usou {champion.ultimate.name}")
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.spell_key), (cid, "ULT"))

    def test_synthetic_ocr_mutations(self):
        for line, cid, key in (
            ("(l4:2S) Ahrl usou Flash", "Ahri", "Flash"),
            ("(14:23) Ahri us0u Flash", "Ahri", "Flash"),
            ("(14:23)  Lux  usou  Exaustao", "Lux", "Exhaust"),
            ("(14:23) Darius usou Te1eporte", "Darius", "Teleport"),
        ):
            with self.subTest(line=line):
                event = self.parser.parse_line(line)
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.spell_key), (cid, key))
                self.assertTrue(looks_like_chat_line(line))

    def test_ultimate_r_ping_and_cast(self):
        # Bare R is visible in the user's real PT-BR capture. The "usou R"
        # variation is reported by the user; it is not visible in that frame.
        for champion in self.assets.champions.values():
            for cast in (False, True):
                with self.subTest(champion=champion.champion_id, cast=cast):
                    body = f"{champion.name}{' usou' if cast else ''} R"
                    event = self.parser.parse_line(f"07:44 Jogador (Kayn): {body}")
                    self.assertIsNotNone(event)
                    self.assertEqual((event.champion_id, event.kind, event.spell_key),
                                     (champion.champion_id, "ultimate", "ULT"))
                    self.assertEqual(event.spell_name, champion.ultimate.name)
                    self.assertEqual(event.game_time, 464)
                    self.assertEqual(event.certain, cast)

    def test_ultimate_r_rejects_unrelated_keys_and_self_pings(self):
        for line in (
            "07:03 Jogador (Kayn): Espere por R - 33s",
            "07:47 Jogador (Kayn): R - Pronto(a)",
            "07:47 Jogador (Kayn): R", "Nasus Q", "Nasus W", "Nasus E",
            "Nasus usou Q", "Nasus usou W", "Nasus usou E", "Nasus usou R agora",
            "Jogador (Kayn): nasus r", "Nasus não usou R",
            "Nasus abusou R", "Nasus R pronto", "Nasus R - Pronto(a)",
        ):
            with self.subTest(line=line):
                self.assertIsNone(self.parser.parse_line(line))
        self.assets.champions["Nasus"].ultimate = None
        self.assertIsNone(self.parser.parse_line("Nasus R"))
        self.assertIsNone(self.parser.parse_line("Nasus usou R"))

    def test_ultimate_r_timer_confirmation_and_tracking_switch(self):
        manager = TimerManager(self.assets, self.settings)
        ping = self.parser.parse_line("Nasus R")
        cast = self.parser.parse_line("Nasus usou R")
        timers = manager.handle_events([ping], force=True)
        self.assertEqual(len(timers), 1)
        self.assertTrue(timers[0].uncertain)
        self.assertTrue(timers[0].approximate)
        manager.handle_events([cast], force=True)
        timers = manager.snapshot()
        self.assertEqual(len(timers), 1)
        self.assertFalse(timers[0].uncertain)
        self.assertEqual(timers[0].spell_name, self.assets.champions["Nasus"].ultimate.name)
        manager.reset()
        self.settings.set("track_ultimates", False, save=False)
        self.assertEqual(manager.handle_events([cast], force=True), [])

    def test_wait_hypotheses_are_uncertain(self):
        for word in ("Aguarde", "Espere"):
            for unit in ("seg.", "segundos", "s", "sec."):
                line = f"(12:04) Jogador (Lux): {word} Ahri Flash - 24S {unit}"
                with self.subTest(line=line):
                    event = self.parser.parse_line(line)
                    self.assertIsNotNone(event)
                    self.assertEqual(event.remaining_seconds, 245)
                    self.assertFalse(event.certain)
                    self.assertTrue(looks_like_chat_line(line))
        manager = TimerManager(self.assets, self.settings)
        event = self.parser.parse_line("Aguarde Ahri Flash - 245 seg.")
        timers = manager.handle_events([event], force=True)
        self.assertEqual(len(timers), 1)
        timer = timers[0]
        self.assertTrue(timer.uncertain)
        self.assertEqual(timer.spell_key, "Flash")

    def test_portuguese_calls_and_canonical_aliases(self):
        for alias, role in (("topo", "TOP"), ("selva", "JUNGLE"), ("caçador", "JUNGLE"),
                            ("meio", "MID"), ("atirador", "ADC"), ("suporte", "SUPPORT"),
                            ("jg", "JUNGLE"), ("sup", "SUPPORT")):
            self.assertEqual(role_from_word(alias), role)
            event = self.parser.parse_line(f"(5:00) Jogador (Lux): {alias} flash 950")
            self.assertEqual((event.target_role, event.spell_key, event.ready_at_game), (role, "Flash", 590))
            self.assertFalse(event.certain)
        for alias, key in (("exa", "Exhaust"), ("ig", "Ignite"), ("tp", "Teleport")):
            self.assertEqual(normalise_spell(alias), key)
            event = self.parser.parse_line(f"Jogador (Lux): jg {alias} 950")
            self.assertEqual(event.spell_key, key)
        self.assertEqual(role_from_word("tp"), "")

    def test_false_positives(self):
        for line in (
            "Jogador (Lux): ahri usou flash", "Jogador (Lux): Ahri usou seu Flash",
            "Ahri abusou Flash", "Ahri recusou Flash", "Ahri causou Flash",
            "Ahri não usou Flash", "Ahri vai usar Flash", "Ahri utilizou Flash",
            "Jogador (Lux): top sem flash", "Jogador (Lux): meio sumiu 30", "gg wp 10",
            "Jogador (Lux): Ahri usou Guilhotina de Noxus", "Você eliminou Ahri!",
            "Aguarde Ahri Flash - 0 seg.", "Aguarde Ahri Flash - 9999 seg.",
            "Aguarde Ahri Flash", "Aguarde Ahri 245 seg.",
            "eu disse Aguarde Ahri Flash - 245 seg.", "Espere Ahri Flash - 245 seg. para lutar",
            "Aguarde Aphelios - 245 seg.", "Aguarde Ziggs - 245 seg.",
        ):
            with self.subTest(line=line):
                self.assertIsNone(self.parser.parse_line(line))

    def test_english_and_french_still_parse(self):
        for locale, name, cast, wait in (
            ("en_US", "Flash", "Ahri used Flash", "Wait Ahri Flash - 245 seconds"),
            ("fr_FR", "Saut éclair", "Ahri a utilisé Saut éclair", "Attendez Ahri Saut éclair - 245 sec."),
        ):
            assets, _ = load_assets()
            assets.locale = locale
            assets.spells["Flash"].name = name
            parser = MessageParser(assets)
            for line in (cast, wait, "Jogador (Lux): " + cast):
                event = parser.parse_line(line)
                self.assertEqual(event.spell_key, "Flash")
                self.assertTrue(event.certain)
            self.assertIsNone(parser.parse_line("Aguarde Ahri Flash - 245 seg."))
            self.assertIsNone(parser.parse_line("Jogador (Lux): Ahri R"))

    def test_countdown_is_localized_without_changing_numeric_format(self):
        timer = ActiveTimer("Ahri", "Ahri", "summoner", "Flash", "Flash", 300, time.monotonic() - 301)
        self.assertEqual(timer.display(), "PRONTO")
        self.assertEqual(COOLDOWNS["Flash"], 300)
        for language in (i18n.ENGLISH, i18n.FRENCH):
            i18n.set_language(language)
            self.assertEqual(timer.display(), "READY")


if __name__ == "__main__":
    unittest.main(verbosity=2)
