from __future__ import annotations

import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from wpur.local_plugins import list_local_plugins
from wpur.plugins_ftp import WordPressFtpPluginReader, connect


# UI temporaire en un seul fichier pour le premier sprint : suffisant pour tester
# le workflow avant de choisir une stack front plus complete.
HTML = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WPUR - Plugins WordPress</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #1f2933;
      --muted: #64748b;
      --line: #d8dee8;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --danger-bg: #fff1f2;
      --danger-text: #be123c;
      --warn-bg: #fff7ed;
      --warn-text: #c2410c;
      --ok-bg: #ecfdf5;
      --ok-text: #047857;
      --info-bg: #eff6ff;
      --info-text: #1d4ed8;
      --soft: #f8fafc;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
    }

    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }

    header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 22px;
    }

    h1 {
      margin: 0 0 6px;
      font-size: 28px;
      line-height: 1.15;
      font-weight: 700;
    }

    .subtitle {
      margin: 0;
      color: var(--muted);
    }

    .status-count {
      min-width: 128px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      padding: 12px 14px;
      text-align: right;
    }

    .status-count strong {
      display: block;
      font-size: 24px;
      line-height: 1;
    }

    .status-count span {
      color: var(--muted);
      font-size: 13px;
    }

    .source-tabs {
      display: inline-grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px;
      margin-bottom: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 4px;
    }

    .source-tabs label {
      margin: 0;
    }

    .source-tabs input {
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }

    .source-tabs span {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 34px;
      border-radius: 6px;
      padding: 0 14px;
      color: var(--muted);
      font-weight: 700;
      cursor: pointer;
    }

    .source-tabs input:checked + span {
      background: var(--accent);
      color: white;
    }

    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      margin-bottom: 16px;
    }

    .ftp-grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr 0.8fr 0.42fr 0.8fr auto;
      gap: 10px;
      margin-bottom: 16px;
    }

    .hidden {
      display: none;
    }

    label {
      display: block;
      font-weight: 700;
      margin-bottom: 7px;
    }

    input,
    select {
      width: 100%;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 12px;
      color: var(--text);
      background: var(--panel);
      font: inherit;
    }

    input:focus,
    select:focus {
      border-color: var(--accent);
      outline: 3px solid rgba(15, 118, 110, 0.16);
    }

    button {
      align-self: end;
      min-height: 42px;
      border: 0;
      border-radius: 8px;
      padding: 0 18px;
      color: white;
      background: var(--accent);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    button:hover { background: var(--accent-dark); }
    button:disabled { cursor: wait; opacity: 0.72; }

    .message {
      display: none;
      margin-bottom: 16px;
      border-radius: 8px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      background: var(--panel);
    }

    .message.error {
      display: block;
      border-color: #fecdd3;
      background: var(--danger-bg);
      color: var(--danger-text);
    }

    .message.success {
      display: block;
      border-color: #bfdbfe;
      background: var(--info-bg);
      color: var(--info-text);
    }

    .scan-summary {
      display: none;
      margin-bottom: 16px;
      color: var(--muted);
      font-size: 14px;
    }

    .scan-summary.visible {
      display: block;
    }

    .result-tools {
      display: none;
      grid-template-columns: 1fr 220px;
      gap: 10px;
      margin-bottom: 16px;
    }

    .result-tools.visible {
      display: grid;
    }

    .quality-strip {
      display: none;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }

    .quality-strip.visible {
      display: grid;
    }

    .quality-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 10px 12px;
    }

    .quality-item strong {
      display: block;
      font-size: 20px;
      line-height: 1;
      margin-bottom: 4px;
    }

    .quality-item span {
      color: var(--muted);
      font-size: 13px;
    }

    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }

    table {
      width: 100%;
      min-width: 760px;
      border-collapse: collapse;
    }

    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
    }

    th {
      color: var(--muted);
      background: #f8fafc;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }

    tr:last-child td { border-bottom: 0; }
    tbody tr:hover { background: var(--soft); }

    .empty {
      padding: 32px 16px;
      color: var(--muted);
      text-align: center;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      border-radius: 999px;
      padding: 0 10px;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }

    .badge.ok {
      background: var(--ok-bg);
      color: var(--ok-text);
    }

    .badge.version_missing {
      background: var(--warn-bg);
      color: var(--warn-text);
    }

    .badge.unreadable {
      background: var(--danger-bg);
      color: var(--danger-text);
    }

    @media (max-width: 720px) {
      main { width: min(100% - 20px, 1120px); padding-top: 18px; }
      header { display: block; }
      .status-count { margin-top: 14px; text-align: left; }
      .toolbar { grid-template-columns: 1fr; }
      .ftp-grid { grid-template-columns: 1fr; }
      .result-tools { grid-template-columns: 1fr; }
      .quality-strip { grid-template-columns: 1fr; }
      button { width: 100%; }
      h1 { font-size: 24px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Plugins WordPress</h1>
        <p class="subtitle">Lecture depuis un chemin local temporaire ou un acces FTP.</p>
      </div>
      <div class="status-count">
        <strong id="plugin-count">0</strong>
        <span>plugins detectes</span>
      </div>
    </header>

    <form id="scan-form">
      <div class="source-tabs" role="radiogroup" aria-label="Source">
        <label>
          <input type="radio" name="source" value="local" checked>
          <span>Local</span>
        </label>
        <label>
          <input type="radio" name="source" value="ftp">
          <span>FTP</span>
        </label>
      </div>

      <div class="toolbar" id="local-fields">
        <div>
          <label for="site-path">Chemin du site WordPress ou du dossier plugins</label>
          <input id="site-path" name="path" placeholder="C:\\chemin\\vers\\wordpress ou C:\\chemin\\vers\\wp-content\\plugins" autocomplete="off">
        </div>
        <button id="local-scan-button" type="submit">Analyser</button>
      </div>

      <div class="ftp-grid hidden" id="ftp-fields">
        <div>
          <label for="ftp-host">Hote FTP</label>
          <input id="ftp-host" name="host" placeholder="ftp.exemple.com" autocomplete="off">
        </div>
        <div>
          <label for="ftp-user">Utilisateur</label>
          <input id="ftp-user" name="user" autocomplete="off">
        </div>
        <div>
          <label for="ftp-password">Mot de passe</label>
          <input id="ftp-password" name="password" type="password" autocomplete="off">
        </div>
        <div>
          <label for="ftp-port">Port</label>
          <input id="ftp-port" name="port" inputmode="numeric" value="21">
        </div>
        <div>
          <label for="ftp-base-path">Chemin WordPress</label>
          <input id="ftp-base-path" name="basePath" placeholder="/" value="/">
        </div>
        <button id="ftp-scan-button" type="submit">Analyser</button>
      </div>
    </form>

    <div id="message" class="message"></div>
    <div id="scan-summary" class="scan-summary"></div>
    <div id="result-tools" class="result-tools">
      <div>
        <label for="plugin-search">Rechercher un plugin</label>
        <input id="plugin-search" placeholder="Nom, identifiant ou version" autocomplete="off">
      </div>
      <div>
        <label for="status-filter">Statut</label>
        <select id="status-filter">
          <option value="">Tous les statuts</option>
          <option value="ok">OK</option>
          <option value="version_missing">Version manquante</option>
          <option value="unreadable">Illisible</option>
        </select>
      </div>
    </div>
    <div id="quality-strip" class="quality-strip" aria-live="polite"></div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Plugin</th>
            <th>Identifiant</th>
            <th>Version actuelle</th>
            <th>Fichier principal</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody id="plugins-body">
          <tr><td class="empty" colspan="5">Renseigne une source pour commencer.</td></tr>
        </tbody>
      </table>
    </div>
  </main>

  <script>
    const form = document.querySelector("#scan-form");
    const localFields = document.querySelector("#local-fields");
    const ftpFields = document.querySelector("#ftp-fields");
    const localButton = document.querySelector("#local-scan-button");
    const ftpButton = document.querySelector("#ftp-scan-button");
    const body = document.querySelector("#plugins-body");
    const message = document.querySelector("#message");
    const summary = document.querySelector("#scan-summary");
    const count = document.querySelector("#plugin-count");
    const resultTools = document.querySelector("#result-tools");
    const qualityStrip = document.querySelector("#quality-strip");
    const searchInput = document.querySelector("#plugin-search");
    const statusFilter = document.querySelector("#status-filter");
    const sourceInputs = [...document.querySelectorAll("input[name='source']")];
    let currentPlugins = [];

    const labels = {
      ok: "OK",
      version_missing: "Version manquante",
      unreadable: "Illisible"
    };

    function showError(text) {
      message.textContent = text;
      message.className = "message error";
    }

    function showSuccess(text) {
      message.textContent = text;
      message.className = "message success";
    }

    function clearError() {
      message.textContent = "";
      message.className = "message";
    }

    function renderEmpty(text) {
      body.innerHTML = `<tr><td class="empty" colspan="5">${text}</td></tr>`;
      count.textContent = "0";
      currentPlugins = [];
      resultTools.className = "result-tools";
      qualityStrip.className = "quality-strip";
    }

    function clearSummary() {
      summary.textContent = "";
      summary.className = "scan-summary";
    }

    function resetFilters() {
      searchInput.value = "";
      statusFilter.value = "";
    }

    function renderSummary(payload) {
      const now = new Date().toLocaleString("fr-FR", {
        dateStyle: "short",
        timeStyle: "short"
      });
      const target = payload.source === "ftp"
        ? `FTP ${payload.host} - chemin ${payload.basePath || "/"}`
        : `Local - ${payload.path}`;

      summary.textContent = `Derniere analyse : ${target} - ${now}`;
      summary.className = "scan-summary visible";
    }

    function renderQuality(plugins) {
      const ok = plugins.filter((plugin) => plugin.status === "ok").length;
      const missing = plugins.filter((plugin) => plugin.status === "version_missing").length;
      const unreadable = plugins.filter((plugin) => plugin.status === "unreadable").length;

      qualityStrip.innerHTML = `
        <div class="quality-item"><strong>${ok}</strong><span>lisibles avec version</span></div>
        <div class="quality-item"><strong>${missing}</strong><span>versions manquantes</span></div>
        <div class="quality-item"><strong>${unreadable}</strong><span>plugins illisibles</span></div>
      `;
      qualityStrip.className = "quality-strip visible";
    }

    function escapeHtml(value) {
      // Les noms de plugins viennent de sites externes, donc le tableau les securise.
      return String(value ?? "-").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function renderPluginRows(plugins) {
      if (!plugins.length) {
        body.innerHTML = `<tr><td class="empty" colspan="5">Aucun plugin ne correspond aux filtres.</td></tr>`;
        return;
      }

      body.innerHTML = plugins.map((plugin) => {
        const status = plugin.status || "unreadable";
        return `
          <tr>
            <td><strong>${escapeHtml(plugin.name || plugin.slug)}</strong></td>
            <td>${escapeHtml(plugin.slug)}</td>
            <td>${escapeHtml(plugin.version)}</td>
            <td>${escapeHtml(plugin.main_file)}</td>
            <td><span class="badge ${escapeHtml(status)}">${escapeHtml(labels[status] || status)}</span></td>
          </tr>
        `;
      }).join("");
    }

    function applyFilters() {
      const term = searchInput.value.trim().toLowerCase();
      const status = statusFilter.value;
      const filtered = currentPlugins.filter((plugin) => {
        const searchable = [
          plugin.name,
          plugin.slug,
          plugin.version,
          plugin.main_file,
          labels[plugin.status] || plugin.status
        ].join(" ").toLowerCase();
        return (!term || searchable.includes(term)) && (!status || plugin.status === status);
      });

      renderPluginRows(filtered);
    }

    function renderPlugins(plugins) {
      currentPlugins = [...plugins].sort((left, right) => {
        const leftName = left.name || left.slug;
        const rightName = right.name || right.slug;
        return leftName.localeCompare(rightName, "fr", { sensitivity: "base" });
      });
      count.textContent = currentPlugins.length;

      if (!currentPlugins.length) {
        renderEmpty("Aucun plugin detecte pour cette source.");
        return;
      }

      resultTools.className = "result-tools visible";
      renderQuality(currentPlugins);
      applyFilters();
    }

    function selectedSource() {
      return sourceInputs.find((input) => input.checked).value;
    }

    function setLoading(isLoading) {
      // Les deux boutons partagent le meme formulaire ; les desactiver evite les doubles lancements.
      localButton.disabled = isLoading;
      ftpButton.disabled = isLoading;
      localButton.textContent = isLoading ? "Analyse..." : "Analyser";
      ftpButton.textContent = isLoading ? "Analyse..." : "Analyser";
    }

    function updateSourceFields() {
      const source = selectedSource();
      localFields.classList.toggle("hidden", source !== "local");
      ftpFields.classList.toggle("hidden", source !== "ftp");
      clearError();
      clearSummary();
      resetFilters();
      renderEmpty("Renseigne une source pour commencer.");
    }

    sourceInputs.forEach((input) => input.addEventListener("change", updateSourceFields));
    searchInput.addEventListener("input", applyFilters);
    statusFilter.addEventListener("change", applyFilters);

    function buildPayload() {
      const source = selectedSource();
      if (source === "ftp") {
        return {
          source,
          host: document.querySelector("#ftp-host").value.trim(),
          user: document.querySelector("#ftp-user").value.trim(),
          password: document.querySelector("#ftp-password").value,
          port: document.querySelector("#ftp-port").value.trim(),
          basePath: document.querySelector("#ftp-base-path").value.trim() || "/"
        };
      }

      return {
        source,
        path: document.querySelector("#site-path").value.trim()
      };
    }

    function validatePayload(payload) {
      if (payload.source === "ftp") {
        const missing = [];
        if (!payload.host) missing.push("hote FTP");
        if (!payload.user) missing.push("utilisateur");
        if (!payload.password) missing.push("mot de passe");
        if (missing.length) {
          return `Champs manquants : ${missing.join(", ")}`;
        }
        if (!/^[0-9]+$/.test(payload.port || "21")) {
          return "Le port FTP doit etre un nombre.";
        }
        return "";
      }

      if (!payload.path) {
        return "Renseigne un chemin local.";
      }
      return "";
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearError();
      clearSummary();

      const requestPayload = buildPayload();
      const validationError = validatePayload(requestPayload);
      if (validationError) {
        renderEmpty("Aucun resultat a afficher.");
        showError(validationError);
        return;
      }

      setLoading(true);

      try {
        // POST evite de mettre les mots de passe FTP dans l'URL et les journaux serveur.
        const response = await fetch("/api/plugins", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestPayload)
        });
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Analyse impossible.");
        }

        renderPlugins(result.plugins);
        renderSummary(requestPayload);
        showSuccess(`${result.plugins.length} plugin(s) detecte(s).`);
      } catch (error) {
        renderEmpty("Aucun resultat a afficher.");
        showError(error.message);
      } finally {
        setLoading(false);
      }
    });
  </script>
</body>
</html>
"""


class WpurRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send_html(HTML)
            return

        if parsed.path == "/api/plugins":
            self._handle_plugins(parse_qs(parsed.query))
            return

        self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/plugins":
            self._handle_plugins_payload(self._read_json_body())
            return

        self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _handle_plugins(self, query: dict[str, list[str]]) -> None:
        # Garde pour les anciens tests locaux qui appellent encore /api/plugins?path=...
        input_path = query.get("path", [""])[0].strip()
        if not input_path:
            self._send_json({"error": "Renseigne un chemin local."}, status=400)
            return

        try:
            plugins = list_local_plugins(input_path)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"plugins": [asdict(plugin) for plugin in plugins]})

    def _handle_plugins_payload(self, payload: dict[str, object]) -> None:
        # L'UI envoie les scans locaux et FTP au meme endpoint pour garder
        # le tableau independant de la source.
        source = str(payload.get("source", "local")).strip()

        if source == "ftp":
            self._handle_ftp_plugins(payload)
            return
        if source != "local":
            self._send_json({"error": "Source inconnue."}, status=400)
            return

        self._handle_local_plugins(payload)

    def _handle_local_plugins(self, payload: dict[str, object]) -> None:
        input_path = str(payload.get("path", "")).strip()
        if not input_path:
            self._send_json({"error": "Renseigne un chemin local."}, status=400)
            return

        try:
            plugins = list_local_plugins(input_path)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        self._send_json({"plugins": [asdict(plugin) for plugin in plugins]})

    def _handle_ftp_plugins(self, payload: dict[str, object]) -> None:
        host = str(payload.get("host", "")).strip()
        user = str(payload.get("user", "")).strip()
        password = str(payload.get("password", ""))
        base_path = str(payload.get("basePath", "/")).strip() or "/"

        try:
            port = int(str(payload.get("port", "21")).strip() or "21")
        except ValueError:
            self._send_json({"error": "Le port FTP doit etre un nombre."}, status=400)
            return

        missing = []
        if not host:
            missing.append("hote FTP")
        if not user:
            missing.append("utilisateur")
        if not password:
            missing.append("mot de passe")
        if missing:
            self._send_json({"error": "Champs manquants : " + ", ".join(missing)}, status=400)
            return

        ftp = None
        try:
            ftp = connect(host, user, password, port, timeout=30)
            plugins = WordPressFtpPluginReader(ftp, base_path).list_plugins()
        except Exception as exc:
            self._send_json({"error": f"Connexion ou lecture FTP impossible : {exc}"}, status=400)
            return
        finally:
            if ftp is not None:
                # Certains serveurs FTP coupent brutalement apres une erreur ;
                # close() sert de secours quand quit() ne peut pas terminer proprement.
                try:
                    ftp.quit()
                except Exception:
                    ftp.close()

        self._send_json({"plugins": [asdict(plugin) for plugin in plugins]})

    def _read_json_body(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length == 0:
            return {}

        data = self.rfile.read(length)
        try:
            payload = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            # Le handler renvoie une erreur de validation au lieu de crasher sur du JSON invalide.
            return {}
        return payload if isinstance(payload, dict) else {}

    def _send_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), WpurRequestHandler)
    print(f"Interface disponible sur http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
