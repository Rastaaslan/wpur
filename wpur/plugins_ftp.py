from __future__ import annotations

import argparse
import csv
import io
import json
import os
import posixpath
import re
import sys
from dataclasses import asdict, dataclass
from ftplib import FTP, error_perm
from typing import Iterable


PLUGIN_HEADER_KEYS = {
    "plugin_name": "Plugin Name",
    "version": "Version",
    "description": "Description",
    "author": "Author",
}


@dataclass(frozen=True)
class PluginInfo:
    slug: str
    name: str | None
    version: str | None
    main_file: str | None
    status: str


def normalize_ftp_path(*parts: str) -> str:
    # Les chemins FTP utilisent le format POSIX, meme quand l'app tourne sous Windows.
    cleaned = [part.strip("/") for part in parts if part and part.strip("/")]
    return "/" + posixpath.join(*cleaned) if cleaned else "/"


def parse_plugin_headers(content: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    # Les metadonnees WordPress sont au debut du fichier PHP principal du plugin.
    # Lire seulement le premier bloc garde les appels FTP legers.
    first_block = content[:8192]

    for field, label in PLUGIN_HEADER_KEYS.items():
        pattern = rf"^[ \t/*#@]*{re.escape(label)}:\s*(.+?)\s*$"
        match = re.search(pattern, first_block, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            headers[field] = match.group(1).strip()

    return headers


class WordPressFtpPluginReader:
    def __init__(self, ftp: FTP, base_path: str = "/") -> None:
        self.ftp = ftp
        self.base_path = normalize_ftp_path(base_path)
        self.plugins_path = normalize_ftp_path(self.base_path, "wp-content", "plugins")

    def list_plugins(self) -> list[PluginInfo]:
        slugs = self._list_plugin_directories()
        return [self._read_plugin(slug) for slug in slugs]

    def _list_plugin_directories(self) -> list[str]:
        # MLSD donne des infos fiables fichier/dossier quand le serveur FTP le supporte.
        entries = self._mlsd_names(self.plugins_path)
        if entries is not None:
            return sorted(name for name, kind in entries if kind == "dir" and not name.startswith("."))

        # Certains hebergeurs utilisent encore de vieux serveurs FTP. Dans ce cas,
        # on entre dans chaque element pour verifier si c'est un dossier de plugin.
        current = self.ftp.pwd()
        try:
            self.ftp.cwd(self.plugins_path)
            names = self.ftp.nlst()
            directories: list[str] = []
            for raw_name in names:
                name = posixpath.basename(raw_name.rstrip("/"))
                if not name or name.startswith("."):
                    continue
                try:
                    self.ftp.cwd(name)
                    self.ftp.cwd("..")
                    directories.append(name)
                except error_perm:
                    continue
            return sorted(directories)
        finally:
            self.ftp.cwd(current)

    def _read_plugin(self, slug: str) -> PluginInfo:
        plugin_path = normalize_ftp_path(self.plugins_path, slug)
        candidates = self._candidate_main_files(plugin_path, slug)

        for filename in candidates:
            remote_file = normalize_ftp_path(plugin_path, filename)
            content = self._read_text(remote_file)
            if content is None:
                continue

            headers = parse_plugin_headers(content)
            if headers.get("plugin_name") or headers.get("version"):
                # Un plugin sans version reste utile a afficher, mais l'UI doit le signaler.
                return PluginInfo(
                    slug=slug,
                    name=headers.get("plugin_name"),
                    version=headers.get("version"),
                    main_file=filename,
                    status="ok" if headers.get("version") else "version_missing",
                )

        return PluginInfo(slug=slug, name=None, version=None, main_file=None, status="unreadable")

    def _candidate_main_files(self, plugin_path: str, slug: str) -> list[str]:
        files = self._mlsd_names(plugin_path)
        php_files: list[str]

        if files is not None:
            php_files = sorted(name for name, kind in files if kind == "file" and name.lower().endswith(".php"))
        else:
            current = self.ftp.pwd()
            try:
                self.ftp.cwd(plugin_path)
                php_files = sorted(
                    posixpath.basename(name)
                    for name in self.ftp.nlst()
                    if posixpath.basename(name).lower().endswith(".php")
                )
            finally:
                self.ftp.cwd(current)

        preferred = f"{slug}.php"
        if preferred in php_files:
            # Les plugins WordPress utilisent souvent nom-du-dossier.php comme fichier principal.
            # On le teste d'abord, puis on inspecte les autres fichiers PHP si besoin.
            return [preferred, *[name for name in php_files if name != preferred]]
        return php_files

    def _mlsd_names(self, path: str) -> list[tuple[str, str]] | None:
        try:
            return [(name, facts.get("type", "")) for name, facts in self.ftp.mlsd(path)]
        except (error_perm, AttributeError):
            # None indique au code appelant d'utiliser la methode FTP plus ancienne.
            return None

    def _read_text(self, remote_file: str) -> str | None:
        buffer = io.BytesIO()
        try:
            self.ftp.retrbinary(f"RETR {remote_file}", buffer.write)
        except error_perm:
            return None

        data = buffer.getvalue()
        # Les en-tetes de plugins sont du texte simple. Le remplacement evite
        # qu'un caractere invalide fasse disparaitre tout le plugin du rapport.
        return data.decode("utf-8", errors="replace")


def connect(host: str, user: str, password: str, port: int, timeout: int) -> FTP:
    ftp = FTP()
    ftp.connect(host=host, port=port, timeout=timeout)
    ftp.login(user=user, passwd=password)
    return ftp


def render_table(plugins: Iterable[PluginInfo]) -> str:
    rows = [["Slug", "Nom", "Version", "Fichier", "Statut"]]
    for plugin in plugins:
        rows.append(
            [
                plugin.slug,
                plugin.name or "-",
                plugin.version or "-",
                plugin.main_file or "-",
                plugin.status,
            ]
        )

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    lines = []
    for index, row in enumerate(rows):
        lines.append("  ".join(value.ljust(widths[column]) for column, value in enumerate(row)))
        if index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def render_csv(plugins: Iterable[PluginInfo]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["slug", "name", "version", "main_file", "status"])
    writer.writeheader()
    for plugin in plugins:
        writer.writerow(asdict(plugin))
    return output.getvalue()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Liste les plugins WordPress installes via FTP.")
    parser.add_argument("--host", default=os.getenv("WPUR_FTP_HOST"), help="Hote FTP")
    parser.add_argument("--user", default=os.getenv("WPUR_FTP_USER"), help="Utilisateur FTP")
    parser.add_argument("--password", default=os.getenv("WPUR_FTP_PASSWORD"), help="Mot de passe FTP")
    parser.add_argument("--port", type=int, default=int(os.getenv("WPUR_FTP_PORT", "21")), help="Port FTP")
    parser.add_argument("--base-path", default=os.getenv("WPUR_FTP_BASE_PATH", "/"), help="Chemin racine WordPress")
    parser.add_argument("--timeout", type=int, default=30, help="Delai de connexion en secondes")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Format de sortie")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    missing = [name for name in ("host", "user", "password") if not getattr(args, name)]
    if missing:
        labels = ", ".join(f"--{name}" for name in missing)
        raise SystemExit(f"Parametres manquants : {labels}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_args(args)

    ftp = connect(args.host, args.user, args.password, args.port, args.timeout)
    try:
        plugins = WordPressFtpPluginReader(ftp, args.base_path).list_plugins()
    finally:
        ftp.quit()

    if args.format == "json":
        print(json.dumps([asdict(plugin) for plugin in plugins], indent=2, ensure_ascii=False))
    elif args.format == "csv":
        print(render_csv(plugins), end="")
    else:
        print(render_table(plugins))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
