"""PT-BR replacement ping reported by the user; no new client capture."""
import _bootstrap  # noqa: F401
from pathlib import Path
import tempfile
import unittest

from message_parser import MessageParser
from ptbr_assets import load_assets
from settings import Settings
from timer_manager import TimerManager


class HextecFlash(unittest.TestCase):
    def setUp(self):
        self.assets, _ = load_assets()
        self.parser = MessageParser(self.assets)
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(Path(self.temp.name) / "settings.json")
        self.settings.update({"locale": "pt_BR", "assume_cosmic_insight": False,
                              "assume_ionian_boots": False}, save=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_reported_announcement_is_confirmed_normal_flash(self):
        for prefix in ("", "(12:04) ", "12:04 Jogador (Lux): "):
            with self.subTest(prefix=prefix):
                line = prefix + "Alistar usou Flash Hextec"
                event = self.parser.parse_line(line)
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.kind, event.spell_key),
                                 ("Alistar", "summoner", "Flash"))
                self.assertEqual(event.spell_name, self.assets.spells["Flash"].name)
                self.assertTrue(event.certain)
                self.assertIsNone(event.remaining_seconds)
                self.assertEqual(event.raw_line, line)

    def test_every_champion_uses_the_same_canonical_spell(self):
        for champion in self.assets.champions.values():
            with self.subTest(champion=champion.champion_id):
                event = self.parser.parse_line(f"12:04 Jogador (Lux): {champion.name} usou Flash Hextec")
                self.assertIsNotNone(event)
                self.assertEqual((event.champion_id, event.spell_key, event.certain),
                                 (champion.champion_id, "Flash", True))

    def test_whitespace_case_and_explicit_synthetic_ocr_variant(self):
        for line in ("Alistar usou flash hextec", "Alistar usou FlashHextec",
                     "Alistar usou Flash  Hextec!", "Alistar us0u F1ash Hextec"):
            with self.subTest(line=line):
                event = self.parser.parse_line(line)
                self.assertIsNotNone(event)
                self.assertEqual((event.spell_key, event.certain), ("Flash", True))

    def test_no_bare_ping_wait_rune_name_extra_words_or_chat_false_positive(self):
        for line in ("Alistar Flash Hextec", "Alistar não usou Flash Hextec",
                     "Alistar abusou Flash Hextec", "Alistar usou Flash Hextec agora",
                     "Alistar usou Flashtração Hextec", "Alistar usou seu Flash Hextec",
                     "Jogador (Lux): Alistar usou flash hextec",
                     "Jogador (Lux): alistar usou Flash Hextec",
                     "Espere Alistar Flash Hextec - 20s",
                     "Alistar Flash Hextec - Pronto(a)"):
            with self.subTest(line=line):
                self.assertIsNone(self.parser.parse_line(line))
        # Existing human timer calls remain uncertain; the cast-only alias
        # must not turn them into confirmed game announcements.
        call = self.parser.parse_line("top flash hextec 950")
        self.assertTrue(call.is_call)
        self.assertFalse(call.certain)

    def test_does_not_expand_english_or_french(self):
        for locale, normal_name, verb in (("en_US", "Flash", "used"),
                                           ("fr_FR", "Saut éclair", "a utilisé")):
            self.assets.locale = locale
            self.assets.spells["Flash"].name = normal_name
            parser = MessageParser(self.assets)
            self.assertIsNone(parser.parse_line(f"12:04 Jogador (Lux): Alistar {verb} Flash Hextec"))
            normal = parser.parse_line(f"12:04 Jogador (Lux): Alistar {verb} {normal_name}")
            self.assertEqual((normal.spell_key, normal.certain), ("Flash", True))

    def test_timer_is_normal_confirmed_flash_with_same_icon_and_duration(self):
        event = self.parser.parse_line("12:04 Jogador (Lux): Alistar usou Flash Hextec")
        manager = TimerManager(self.assets, self.settings)
        manager.handle_events([event], force=True)
        timer, = manager.snapshot()
        self.assertEqual((timer.spell_key, timer.spell_name, timer.duration), ("Flash", "Flash", 300))
        self.assertFalse(timer.uncertain)
        self.assertFalse(timer.approximate)
        self.assertEqual(self.assets.spells[timer.spell_key].ddragon_id, "SummonerFlash")

    def test_hextec_and_normal_announcement_deduplicate_the_same_cast(self):
        normal = self.parser.parse_line("12:04 Alistar usou Flash")
        hextec = self.parser.parse_line("12:04 Alistar usou Flash Hextec")
        self.assertEqual(normal.signature, hextec.signature)
        manager = TimerManager(self.assets, self.settings)
        for events in ([normal, hextec], [hextec, normal]):
            manager.reset()
            manager.handle_events(events, force=True)
            self.assertEqual(manager.active_count(), 1)
            self.assertEqual(len(manager.history), 1)

    def test_confirms_uncertain_flash_and_preserves_existing_modifiers(self):
        manager = TimerManager(self.assets, self.settings)
        bare = self.parser.parse_line("12:04 Alistar Flash")
        confirmed = self.parser.parse_line("12:04 Alistar usou Flash Hextec")
        manager.handle_events([bare], force=True)
        self.assertTrue(manager.snapshot()[0].uncertain)
        manager.handle_events([confirmed], force=True)
        self.assertFalse(manager.snapshot()[0].uncertain)
        self.settings.set("assume_cosmic_insight", True, save=False)
        manager.reset()
        manager.handle_events([confirmed], force=True)
        self.assertEqual(manager.snapshot()[0].duration, 246)  # unchanged legacy modifier


if __name__ == "__main__":
    unittest.main(verbosity=2)
