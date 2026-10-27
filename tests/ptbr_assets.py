"""Offline assets derived from Riot JSON, with the production loader and cache keys."""
import json
from pathlib import Path

from riot_assets import RiotAssets

FIXTURE = json.loads((Path(__file__).parent / "fixtures/pt_BR/ddragon.json").read_text("utf-8"))


def load_assets():
    assets = RiotAssets("pt_BR")
    assets.version = FIXTURE["version"]
    requests = []

    def cached(name, url):
        requests.append((name, url))
        return FIXTURE["summoners"] if "/summoner.json" in url else FIXTURE["champions"]

    assets._cached_json = cached
    assets._load_summoner_spells()
    assets._load_champions()
    assets.ready = True
    return assets, requests
