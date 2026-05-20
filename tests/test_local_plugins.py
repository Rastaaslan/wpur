from pathlib import Path

import pytest

from wpur.local_plugins import list_local_plugins, resolve_plugins_path


def test_resolve_plugins_path_accepts_wordpress_root(tmp_path: Path) -> None:
    plugins_path = tmp_path / "wp-content" / "plugins"
    plugins_path.mkdir(parents=True)

    assert resolve_plugins_path(str(tmp_path)) == plugins_path


def test_resolve_plugins_path_accepts_plugins_directory(tmp_path: Path) -> None:
    plugins_path = tmp_path / "plugins"
    plugins_path.mkdir()

    assert resolve_plugins_path(str(plugins_path)) == plugins_path


def test_list_local_plugins_reads_versions(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "wp-content" / "plugins" / "contact-form"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "contact-form.php").write_text(
        """<?php
/**
 * Plugin Name: Contact Form
 * Version: 5.1.0
 */
""",
        encoding="utf-8",
    )

    plugins = list_local_plugins(str(tmp_path))

    assert len(plugins) == 1
    assert plugins[0].slug == "contact-form"
    assert plugins[0].name == "Contact Form"
    assert plugins[0].version == "5.1.0"


def test_resolve_plugins_path_rejects_unknown_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        resolve_plugins_path(str(tmp_path))
