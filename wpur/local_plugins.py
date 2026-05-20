from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wpur.plugins_ftp import parse_plugin_headers


@dataclass(frozen=True)
class LocalPluginInfo:
    slug: str
    name: str | None
    version: str | None
    main_file: str | None
    status: str


def resolve_plugins_path(input_path: str) -> Path:
    root = Path(input_path).expanduser().resolve()
    direct_plugins = root / "wp-content" / "plugins"

    # Pour les tests locaux, on peut coller la racine WordPress ou directement
    # le dossier plugins. Les deux arrivent au meme scanner.
    if direct_plugins.is_dir():
        return direct_plugins
    if root.name == "plugins" and root.is_dir():
        return root

    raise FileNotFoundError(f"Dossier plugins introuvable depuis : {root}")


def list_local_plugins(input_path: str) -> list[LocalPluginInfo]:
    plugins_path = resolve_plugins_path(input_path)
    plugins: list[LocalPluginInfo] = []

    for plugin_dir in sorted(path for path in plugins_path.iterdir() if path.is_dir() and not path.name.startswith(".")):
        plugins.append(read_local_plugin(plugin_dir))

    return plugins


def read_local_plugin(plugin_dir: Path) -> LocalPluginInfo:
    candidates = candidate_main_files(plugin_dir)

    for php_file in candidates:
        try:
            content = php_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        headers = parse_plugin_headers(content)
        if headers.get("plugin_name") or headers.get("version"):
            # On garde les donnees partielles visibles : une version manquante est
            # une alerte, pas une raison de retirer le plugin du rapport.
            return LocalPluginInfo(
                slug=plugin_dir.name,
                name=headers.get("plugin_name"),
                version=headers.get("version"),
                main_file=php_file.name,
                status="ok" if headers.get("version") else "version_missing",
            )

    return LocalPluginInfo(slug=plugin_dir.name, name=None, version=None, main_file=None, status="unreadable")


def candidate_main_files(plugin_dir: Path) -> list[Path]:
    php_files = sorted(path for path in plugin_dir.iterdir() if path.is_file() and path.suffix.lower() == ".php")
    preferred = plugin_dir / f"{plugin_dir.name}.php"

    if preferred in php_files:
        # La plupart des plugins suivent cette convention, c'est donc le meilleur premier essai.
        return [preferred, *[path for path in php_files if path != preferred]]
    return php_files
