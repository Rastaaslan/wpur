from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from typing import Callable, Iterable, TypeVar
from urllib.parse import urlencode
from urllib.request import Request, urlopen


WORDPRESS_PLUGIN_INFO_URL = "https://api.wordpress.org/plugins/info/1.2/"
STATUS_UP_TO_DATE = "up_to_date"
STATUS_UPDATE_AVAILABLE = "update_available"
STATUS_LATEST_UNKNOWN = "latest_unknown"
STATUS_INSTALLED_UNKNOWN = "installed_unknown"


@dataclass(frozen=True)
class PluginUpdateInfo:
    latest_version: str | None
    update_status: str
    update_source: str | None


PluginT = TypeVar("PluginT")
VersionLookup = Callable[[str], str | None]


def fetch_wordpress_latest_version(slug: str, timeout: int = 6) -> str | None:
    query = urlencode({"action": "plugin_information", "request[slug]": slug})
    request = Request(
        f"{WORDPRESS_PLUGIN_INFO_URL}?{query}",
        headers={"User-Agent": "WPUR/0.2"},
    )

    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        return None
    version = payload.get("version")
    return str(version).strip() if version else None


def enrich_plugins_with_updates(
    plugins: Iterable[PluginT],
    lookup_latest_version: VersionLookup = fetch_wordpress_latest_version,
) -> list[PluginT]:
    enriched: list[PluginT] = []
    cache: dict[str, str | None] = {}

    for plugin in plugins:
        slug = str(getattr(plugin, "slug"))
        installed_version = getattr(plugin, "version", None)

        if not installed_version:
            enriched.append(with_update_info(plugin, PluginUpdateInfo(None, STATUS_INSTALLED_UNKNOWN, None)))
            continue

        if slug not in cache:
            try:
                cache[slug] = lookup_latest_version(slug)
            except Exception:
                cache[slug] = None

        latest_version = cache[slug]
        if not latest_version:
            enriched.append(with_update_info(plugin, PluginUpdateInfo(None, STATUS_LATEST_UNKNOWN, None)))
            continue

        enriched.append(
            with_update_info(
                plugin,
                PluginUpdateInfo(
                    latest_version=latest_version,
                    update_status=compare_versions(str(installed_version), latest_version),
                    update_source="wordpress.org",
                ),
            )
        )

    return enriched


def with_update_info(plugin: PluginT, update: PluginUpdateInfo) -> PluginT:
    return replace(
        plugin,
        latest_version=update.latest_version,
        update_status=update.update_status,
        update_source=update.update_source,
    )


def compare_versions(installed_version: str, latest_version: str) -> str:
    installed = installed_version.strip()
    latest = latest_version.strip()

    if not installed:
        return STATUS_INSTALLED_UNKNOWN
    if not latest:
        return STATUS_LATEST_UNKNOWN
    if normalize_version(installed) == normalize_version(latest):
        return STATUS_UP_TO_DATE

    installed_parts = numeric_parts(installed)
    latest_parts = numeric_parts(latest)
    if not installed_parts or not latest_parts:
        return STATUS_LATEST_UNKNOWN

    length = max(len(installed_parts), len(latest_parts))
    installed_parts = installed_parts + [0] * (length - len(installed_parts))
    latest_parts = latest_parts + [0] * (length - len(latest_parts))

    if installed_parts < latest_parts:
        return STATUS_UPDATE_AVAILABLE
    return STATUS_UP_TO_DATE


def normalize_version(version: str) -> str:
    return version.strip().lower().lstrip("v")


def numeric_parts(version: str) -> list[int]:
    return [int(part) for part in re.findall(r"\d+", version)]
