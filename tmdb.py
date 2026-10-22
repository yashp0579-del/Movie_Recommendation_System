"""Fetch real posters, overview and streaming availability from TMDB (free API).

Speed-ups:
  * all movies on screen are fetched IN PARALLEL (8 at a time)
  * results are cached in memory AND in poster_cache.json, so each movie is
    downloaded only once - even after you restart the app
  * smaller poster size (w342) loads faster
"""
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter

BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w342"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster_cache.json")

_lock = threading.Lock()
_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=16, pool_maxsize=16))
_cache = None
_key_status = {}


class TMDBError(Exception):
    """Temporary failure (network, rate limit, bad key). Never cached."""


def _load():
    global _cache
    if _cache is None:
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}
    return _cache


def _save():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f)
    except Exception:
        pass


def clear_cache():
    global _cache
    _cache = {}
    _key_status.clear()
    try:
        os.remove(CACHE_FILE)
    except OSError:
        pass


def _get(path, api_key, params=None, retries=3):
    params = dict(params or {})
    params["api_key"] = api_key
    last = None
    for i in range(retries):
        try:
            r = _session.get(f"{BASE}{path}", params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 401:
                raise TMDBError("Invalid API key (use the short 'API Key', not the long token).")
            if r.status_code == 429:
                time.sleep(1.0 * (i + 1))
                last = TMDBError("Rate limited by TMDB.")
                continue
            last = TMDBError(f"TMDB returned status {r.status_code}.")
        except requests.RequestException as e:
            last = TMDBError(str(e))
            time.sleep(0.4 * (i + 1))
    raise last or TMDBError("Unknown error")


def check_key(api_key):
    """(ok, message). Checked once per key, not on every click."""
    if not api_key:
        return False, "No key entered."
    if api_key in _key_status:
        return _key_status[api_key]
    try:
        _get("/configuration", api_key, retries=1)
        result = (True, "Key is valid.")
    except TMDBError as e:
        result = (False, str(e))
    if result[0]:
        _key_status[api_key] = result
    return result


def _find_movie(title, year, api_key):
    tries = [
        {"query": title, "year": year},
        {"query": title},
        {"query": title, "primary_release_year": year},
    ]
    if ":" in title:
        tries.append({"query": title.split(":")[0].strip(), "year": year})
    fallback = None
    for params in tries:
        for m in _get("/search/movie", api_key, params).get("results", []):
            if not m.get("poster_path"):
                continue
            ry = (m.get("release_date") or "0000")[:4]
            if ry.isdigit() and abs(int(ry) - year) <= 1:
                return m
            fallback = fallback or m
    return fallback


def _fetch_one(title, year, api_key, region):
    m = _find_movie(title, int(year), api_key)
    info = {"poster": None, "overview": "", "stream": [], "rent": [], "buy": [], "link": None}
    if not m:
        return info
    info["poster"] = IMG + m["poster_path"] if m.get("poster_path") else None
    info["overview"] = m.get("overview", "")
    try:
        p = _get(f"/movie/{m['id']}/watch/providers", api_key)
        reg = p.get("results", {}).get(region, {})
        info["stream"] = [x["provider_name"] for x in reg.get("flatrate", [])]
        info["rent"] = [x["provider_name"] for x in reg.get("rent", [])]
        info["buy"] = [x["provider_name"] for x in reg.get("buy", [])]
        info["link"] = reg.get("link")
    except TMDBError:
        pass
    return info


def fetch_many(items, api_key, region="IN"):
    """items: list of (title, year). Returns {(title, year): info or None}."""
    if not api_key:
        return {}
    api_key = api_key.strip()
    cache = _load()
    out, todo = {}, []
    for t, y in items:
        k = f"{t}|{y}|{region}"
        if k in cache:
            out[(t, y)] = cache[k]
        else:
            todo.append((t, y))

    if todo:
        def work(item):
            try:
                return item, _fetch_one(item[0], item[1], api_key, region)
            except TMDBError:
                return item, None

        with ThreadPoolExecutor(max_workers=8) as ex:
            for item, info in ex.map(work, todo):
                if info is not None:
                    with _lock:
                        cache[f"{item[0]}|{item[1]}|{region}"] = info
                out[item] = info
        with _lock:
            _save()
    return out