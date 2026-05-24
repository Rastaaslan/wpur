from wpur.local_plugins import LocalPluginInfo
from wpur.update_checker import compare_versions, enrich_plugins_with_updates


def test_compare_versions_detects_update_available() -> None:
    assert compare_versions("1.2.3", "1.3.0") == "update_available"


def test_compare_versions_detects_up_to_date() -> None:
    assert compare_versions("2.0.0", "2.0") == "up_to_date"


def test_compare_versions_ignores_v_prefix() -> None:
    assert compare_versions("v2.0.0", "2.0") == "up_to_date"


def test_compare_versions_handles_missing_installed_version() -> None:
    assert compare_versions("", "2.0.0") == "installed_unknown"


def test_enrich_plugins_with_updates_adds_latest_version() -> None:
    plugin = LocalPluginInfo(
        slug="demo-plugin",
        name="Demo Plugin",
        version="1.0.0",
        main_file="demo-plugin.php",
        status="ok",
    )

    enriched = enrich_plugins_with_updates([plugin], lambda slug: "1.2.0")

    assert enriched[0].latest_version == "1.2.0"
    assert enriched[0].update_status == "update_available"
    assert enriched[0].update_source == "wordpress.org"


def test_enrich_plugins_with_updates_keeps_unknown_public_version() -> None:
    plugin = LocalPluginInfo(
        slug="private-plugin",
        name="Private Plugin",
        version="1.0.0",
        main_file="private-plugin.php",
        status="ok",
    )

    enriched = enrich_plugins_with_updates([plugin], lambda slug: None)

    assert enriched[0].latest_version is None
    assert enriched[0].update_status == "latest_unknown"
    assert enriched[0].update_source is None


def test_enrich_plugins_with_updates_keeps_plugin_when_lookup_fails() -> None:
    plugin = LocalPluginInfo(
        slug="private-plugin",
        name="Private Plugin",
        version="1.0.0",
        main_file="private-plugin.php",
        status="ok",
    )

    def failing_lookup(slug: str) -> str | None:
        raise TimeoutError("API indisponible")

    enriched = enrich_plugins_with_updates([plugin], failing_lookup)

    assert enriched[0].slug == "private-plugin"
    assert enriched[0].update_status == "latest_unknown"


def test_enrich_plugins_with_updates_caches_lookup_by_slug() -> None:
    plugins = [
        LocalPluginInfo("same-plugin", "Same Plugin", "1.0.0", "same-plugin.php", "ok"),
        LocalPluginInfo("same-plugin", "Same Plugin Copy", "1.0.0", "same-plugin.php", "ok"),
    ]
    calls = []

    def lookup(slug: str) -> str | None:
        calls.append(slug)
        return "1.0.0"

    enrich_plugins_with_updates(plugins, lookup)

    assert calls == ["same-plugin"]
