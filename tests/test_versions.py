from pathlib import Path

from wpur.versions import (
    PluginVersionLookup,
    VersionCache,
    compare_versions,
    determine_update_status,
    enrich_plugin_with_latest,
    enrich_plugins_with_latest,
)


def test_compare_versions_handles_numeric_segments() -> None:
    assert compare_versions("1.10.0", "1.9.9") == 1
    assert compare_versions("2.0", "2.0.0") == 0
    assert compare_versions("3.21.0", "3.22.1") == -1


def test_determine_update_status_distinguishes_core_states() -> None:
    assert determine_update_status("1.0.0", "1.0.0", "public") == "up_to_date"
    assert determine_update_status("1.0.0", "1.1.0", "public") == "update_available"
    assert determine_update_status("1.2.0", "1.1.0", "public") == "newer_than_public"
    assert determine_update_status("1.0.0", None, "premium_custom") == "premium_custom"
    assert determine_update_status("1.0.0", None, "error") == "error"
    assert determine_update_status(None, "1.0.0", "public") == "unknown"


def test_enrich_plugin_with_latest_adds_latest_version_and_status() -> None:
    def lookup(slug: str) -> PluginVersionLookup:
        return PluginVersionLookup(slug=slug, latest_version="5.2.0", remote_status="public", fetched_at="2026-05-28T10:00:00Z")

    plugin = {
        "slug": "contact-form",
        "name": "Contact Form",
        "version": "5.1.0",
        "main_file": "contact-form.php",
        "status": "ok",
    }

    enriched = enrich_plugin_with_latest(plugin, lookup=lookup)

    assert enriched["installed_version"] == "5.1.0"
    assert enriched["latest_version"] == "5.2.0"
    assert enriched["update_status"] == "update_available"
    assert enriched["remote_status"] == "public"
    assert enriched["read_status"] == "ok"
    assert enriched["version_checked_at"] == "2026-05-28T10:00:00Z"


def test_enrich_plugin_marks_absent_public_plugin_as_premium_custom() -> None:
    def lookup(slug: str) -> PluginVersionLookup:
        return PluginVersionLookup(slug=slug, latest_version=None, remote_status="premium_custom", error="Not found")

    enriched = enrich_plugin_with_latest({"slug": "private-plugin", "version": "1.0.0"}, lookup=lookup)

    assert enriched["update_status"] == "premium_custom"
    assert enriched["version_error"] == "Not found"


def test_enrich_plugins_keeps_input_order() -> None:
    versions = {
        "alpha": "1.1.0",
        "beta": "2.0.0",
    }

    def lookup(slug: str) -> PluginVersionLookup:
        return PluginVersionLookup(slug=slug, latest_version=versions[slug], remote_status="public")

    enriched = enrich_plugins_with_latest(
        [{"slug": "alpha", "version": "1.0.0"}, {"slug": "beta", "version": "2.0.0"}],
        lookup=lookup,
        max_workers=2,
    )

    assert [plugin["slug"] for plugin in enriched] == ["alpha", "beta"]
    assert [plugin["update_status"] for plugin in enriched] == ["update_available", "up_to_date"]


def test_version_cache_returns_fresh_and_stale_entries(tmp_path: Path) -> None:
    cache = VersionCache(tmp_path / "versions.json", ttl_seconds=0)
    cache.set(PluginVersionLookup("akismet", "5.3", "public", fetched_at="2026-05-28T10:00:00Z"))

    assert cache.get("akismet").latest_version == "5.3"
    assert cache.get("akismet", allow_stale=True).source == "cache"

    data = cache.load()
    data["akismet"]["fetched_timestamp"] = 0
    cache.save()

    stale_cache = VersionCache(tmp_path / "versions.json", ttl_seconds=1)
    assert stale_cache.get("akismet") is None
    assert stale_cache.get("akismet", allow_stale=True).source == "cache_stale"
