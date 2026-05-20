from wpur.plugins_ftp import normalize_ftp_path, parse_plugin_headers


def test_parse_plugin_headers_reads_wordpress_metadata() -> None:
    content = """<?php
/**
 * Plugin Name: Example Plugin
 * Description: Demo
 * Version: 1.2.3
 * Author: Studio
 */
"""

    headers = parse_plugin_headers(content)

    assert headers["plugin_name"] == "Example Plugin"
    assert headers["version"] == "1.2.3"
    assert headers["author"] == "Studio"


def test_parse_plugin_headers_accepts_loose_comment_prefixes() -> None:
    content = """<?php
# Plugin Name: Loose Plugin
# Version: 2.0.0
"""

    headers = parse_plugin_headers(content)

    assert headers["plugin_name"] == "Loose Plugin"
    assert headers["version"] == "2.0.0"


def test_normalize_ftp_path() -> None:
    assert normalize_ftp_path("/", "wp-content", "plugins") == "/wp-content/plugins"
    assert normalize_ftp_path("/www/", "/wp-content/", "plugins") == "/www/wp-content/plugins"
    assert normalize_ftp_path("/") == "/"
