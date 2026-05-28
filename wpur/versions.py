from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, is_dataclass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Mapping


WORDPRESS_PLUGIN_INFO_URL = "https://api.wordpress.org/plugins/info/1.0/{slug}.json"
DEFAULT_CACHE_TTL_SECONDS = 24 * 60 * 60


@dataclass(frozen=True)
class PluginVersionLookup:
    slug: str
    latest_version: str | None
    remote_status: str
    error: str | None = None
    fetched_at: str | None = None
    source: str = "api"


def default_cache_path() -> Path:
    return Path(os.getenv("WPUR_VERSION_CACHE", ".wpur-cache/plugin_versions.json")).expanduser()


def _now_timestamp() -> int:
    return int(time.time())


def _timestamp_label(timestamp: int | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp or _now_timestamp()))


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {
        name: getattr(value, name)
        for name in dir(value)
        if not name.startswith("_") and not callable(getattr(value, name))
    }


class VersionCache:
    def __init__(self, path: str | Path | None = None, ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS) -> None:
        self.path = default_cache_path() if path is None else Path(path).expanduser()
        self.ttl_seconds = ttl_seconds
        self._data: dict[str, dict[str, Any]] | None = None
        self._lock = Lock()

    def load(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            if self._data is not None:
                return self._data
            if not self.path.exists():
                self._data = {}
                return self._data

            try:
                decoded = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self._data = {}
                return self._data

            self._data = decoded if isinstance(decoded, dict) else {}
            return self._data

    def save(self) -> None:
        with self._lock:
            if self._data is None:
                return
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    def get(self, slug: str, allow_stale: bool = False) -> PluginVersionLookup | None:
        entry = self.load().get(slug)
        if not entry:
            return None

        fetched_timestamp = int(entry.get("fetched_timestamp") or 0)
        is_stale = self.ttl_seconds > 0 and (_now_timestamp() - fetched_timestamp) > self.ttl_seconds
        if is_stale and not allow_stale:
            return None

        return PluginVersionLookup(
            slug=slug,
            latest_version=entry.get("latest_version"),
            remote_status=str(entry.get("remote_status") or "unknown"),
            error=entry.get("error"),
            fetched_at=entry.get("fetched_at"),
            source="cache_stale" if is_stale else "cache",
        )

    def set(self, lookup: PluginVersionLookup) -> None:
        timestamp = _now_timestamp()
        data = self.load()
        with self._lock:
            data[lookup.slug] = {
                "latest_version": lookup.latest_version,
                "remote_status": lookup.remote_status,
                "error": lookup.error,
                "fetched_at": lookup.fetched_at or _timestamp_label(timestamp),
                "fetched_timestamp": timestamp,
            }
        self.save()


class WordPressPluginVersionClient:
    def __init__(
        self,
        cache_path: str | Path | None = None,
        timeout: int = 10,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
        use_cache: bool = True,
    ) -> None:
        self.timeout = timeout
        self.use_cache = use_cache
        self.cache = VersionCache(cache_path, ttl_seconds=ttl_seconds) if use_cache else None

    def lookup(self, slug: str, refresh: bool = False) -> PluginVersionLookup:
        cleaned_slug = slug.strip()
        if not cleaned_slug:
            return PluginVersionLookup(slug=slug, latest_version=None, remote_status="unknown", error="Slug vide.")

        if self.cache is not None and not refresh:
            cached = self.cache.get(cleaned_slug)
            if cached is not None:
                return cached

        result = fetch_wordpress_plugin_version(cleaned_slug, timeout=self.timeout)
        if self.cache is not None and result.remote_status != "error":
            self.cache.set(result)
        elif self.cache is not None and result.remote_status == "error":
            stale = self.cache.get(cleaned_slug, allow_stale=True)
            if stale is not None:
                return PluginVersionLookup(
                    slug=stale.slug,
                    latest_version=stale.latest_version,
                    remote_status=stale.remote_status,
                    error=f"Cache stale utilise apres erreur reseau : {result.error}",
                    fetched_at=stale.fetched_at,
                    source="cache_stale",
                )
        return result


def fetch_wordpress_plugin_version(slug: str, timeout: int = 10) -> PluginVersionLookup:
    cleaned_slug = slug.strip()
    if not cleaned_slug:
        return PluginVersionLookup(slug=slug, latest_version=None, remote_status="unknown", error="Slug vide.")

    url = WORDPRESS_PLUGIN_INFO_URL.format(slug=urllib.parse.quote(cleaned_slug, safe=""))
    request = urllib.request.Request(url, headers={"User-Agent": "WPUR/0.1"})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return PluginVersionLookup(
                cleaned_slug,
                None,
                "premium_custom",
                "Plugin absent du repertoire public WordPress.org.",
                _timestamp_label(),
            )
        return PluginVersionLookup(cleaned_slug, None, "error", f"Erreur HTTP WordPress.org : {exc.code}", _timestamp_label())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return PluginVersionLookup(cleaned_slug, None, "error", str(exc), _timestamp_label())

    if not isinstance(payload, dict):
        return PluginVersionLookup(cleaned_slug, None, "error", "Reponse WordPress.org inattendue.", _timestamp_label())

    if payload.get("error"):
        return PluginVersionLookup(cleaned_slug, None, "premium_custom", str(payload.get("error")), _timestamp_label())

    latest_version = payload.get("version")
    if not latest_version:
        return PluginVersionLookup(
            cleaned_slug,
            None,
            "unknown",
            "Version publique absente de la reponse.",
            _timestamp_label(),
        )

    return PluginVersionLookup(cleaned_slug, str(latest_version), "public", fetched_at=_timestamp_label())


def _version_tokens(version: str) -> list[tuple[int, int | str]]:
    tokens: list[tuple[int, int | str]] = []
    for token in re.findall(r"\d+|[a-zA-Z]+", version.lower()):
        if token.isdigit():
            tokens.append((0, int(token)))
        else:
            tokens.append((1, token))
    return tokens


def compare_versions(left: str, right: str) -> int:
    left_tokens = _version_tokens(left)
    right_tokens = _version_tokens(right)
    max_length = max(len(left_tokens), len(right_tokens))

    for index in range(max_length):
        left_token = left_tokens[index] if index < len(left_tokens) else (0, 0)
        right_token = right_tokens[index] if index < len(right_tokens) else (0, 0)
        if left_token == right_token:
            continue
        return -1 if left_token < right_token else 1
    return 0


def determine_update_status(
    installed_version: str | None,
    latest_version: str | None,
    remote_status: str,
) -> str:
    if remote_status == "premium_custom":
        return "premium_custom"
    if remote_status == "error":
        return "error"
    if not installed_version or not latest_version:
        return "unknown"

    comparison = compare_versions(str(installed_version), str(latest_version))
    if comparison == 0:
        return "up_to_date"
    if comparison < 0:
        return "update_available"
    return "newer_than_public"


def enrich_plugin_with_latest(
    plugin: Any,
    lookup: Callable[[str], PluginVersionLookup] | WordPressPluginVersionClient | None = None,
    refresh: bool = False,
) -> dict[str, Any]:
    data = _as_dict(plugin)
    slug = str(data.get("slug") or "").strip()
    installed_version = data.get("installed_version") or data.get("version")

    if lookup is None:
        result = WordPressPluginVersionClient().lookup(slug, refresh=refresh)
    elif isinstance(lookup, WordPressPluginVersionClient):
        result = lookup.lookup(slug, refresh=refresh)
    else:
        result = lookup(slug)

    lookup_data = _as_dict(result)
    remote_status = str(lookup_data.get("remote_status") or "unknown")
    latest_version = lookup_data.get("latest_version")

    enriched = dict(data)
    if "status" in data and "read_status" not in enriched:
        enriched["read_status"] = data["status"]
    if "version" not in enriched and installed_version is not None:
        enriched["version"] = installed_version
    enriched["installed_version"] = installed_version
    enriched["latest_version"] = latest_version
    enriched["remote_status"] = remote_status
    enriched["update_status"] = determine_update_status(installed_version, latest_version, remote_status)
    enriched["version_checked_at"] = lookup_data.get("fetched_at")
    enriched["version_source"] = lookup_data.get("source") or "api"
    if lookup_data.get("error"):
        enriched["version_error"] = lookup_data["error"]
    return enriched


def enrich_plugins_with_latest(
    plugins: list[Any],
    lookup: Callable[[str], PluginVersionLookup] | WordPressPluginVersionClient | None = None,
    refresh: bool = False,
    max_workers: int = 8,
) -> list[dict[str, Any]]:
    if not plugins:
        return []

    if max_workers <= 1:
        return [enrich_plugin_with_latest(plugin, lookup=lookup, refresh=refresh) for plugin in plugins]

    worker_count = min(max_workers, len(plugins))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(lambda plugin: enrich_plugin_with_latest(plugin, lookup=lookup, refresh=refresh), plugins))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recupere les versions publiques WordPress.org de plugins.")
    parser.add_argument("slugs", nargs="+", help="Slugs de plugins WordPress.org")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    parser.add_argument("--refresh", action="store_true", help="Ignore le cache local")
    parser.add_argument("--no-cache", action="store_true", help="Desactive le cache local")
    parser.add_argument("--cache-path", default=None, help="Chemin du cache JSON")
    parser.add_argument("--timeout", type=int, default=10, help="Delai API WordPress.org en secondes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = WordPressPluginVersionClient(cache_path=args.cache_path, timeout=args.timeout, use_cache=not args.no_cache)
    results = [asdict(client.lookup(slug, refresh=args.refresh)) for slug in args.slugs]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0

    for result in results:
        print(f"{result['slug']}: {result['latest_version'] or '-'} ({result['remote_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
