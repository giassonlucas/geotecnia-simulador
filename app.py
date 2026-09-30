"""Run the local geotechnical simulator with `python app.py`."""

from __future__ import annotations

import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from calculation.model import DEFAULTS, simulate
from reporting import make_pdf_report


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8501"))
MAX_REQUEST_BYTES = 12_000_000


class SimulatorHandler(BaseHTTPRequestHandler):
    server_version = "GeotecniaSimulator/1.0"

    def _send(self, status: int, body: bytes, content_type: str, filename: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            target = STATIC / "index.html"
            content_type = "text/html; charset=utf-8"
        elif self.path == "/app.js":
            target = STATIC / "app.js"
            content_type = "text/javascript; charset=utf-8"
        elif self.path == "/calculation.js":
            target = STATIC / "calculation.js"
            content_type = "text/javascript; charset=utf-8"
        elif self.path == "/styles.css":
            target = STATIC / "styles.css"
            content_type = "text/css; charset=utf-8"
        elif self.path in ("/manifest.webmanifest", "/sw.js", "/icon-180.png", "/icon-192.png", "/icon-512.png"):
            name = self.path.rsplit("/", 1)[-1]
            target = STATIC / name
            content_type = {"manifest.webmanifest": "application/manifest+json", "sw.js": "text/javascript; charset=utf-8", "icon-180.png": "image/png", "icon-192.png": "image/png", "icon-512.png": "image/png"}[name]
        elif self.path == "/api/health":
            self._json(200, {"status": "ok", "defaults": DEFAULTS})
            return
        else:
            self._json(404, {"error": "Rota não encontrada."})
            return
        if not target.is_file():
            self._json(404, {"error": "Arquivo da interface não encontrado."})
            return
        self._send(200, target.read_bytes(), content_type)

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "Cabeçalho Content-Length inválido."})
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self._json(413, {"error": "Corpo da requisição vazio ou grande demais."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "Não foi possível ler os dados enviados."})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "Os dados precisam ser enviados como objeto JSON."})
            return

        if self.path == "/api/simulate":
            try:
                result = simulate(payload)
            except ValueError as exc:
                self._json(422, {"error": str(exc)})
                return
            except Exception as exc:  # Keep internal details in server logs, not the page.
                self.log_error("Falha de cálculo: %r", exc)
                self._json(500, {"error": "Falha durante o cálculo. Revise os dados e tente novamente."})
                return
            self._json(200, result)
            return

        if self.path == "/api/report":
            result = payload.get("result")
            if not isinstance(result, dict):
                self._json(400, {"error": "O resultado da simulação não foi enviado."})
                return
            try:
                pdf = make_pdf_report(result)
            except RuntimeError as exc:
                self._json(501, {"error": str(exc)})
                return
            except Exception as exc:
                self.log_error("Falha ao gerar PDF: %r", exc)
                self._json(500, {"error": "Falha ao gerar o relatório PDF."})
                return
            self._send(200, pdf, "application/pdf", "relatorio_geotecnia.pdf")
            return

        self._json(404, {"error": "Rota não encontrada."})

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def log_error(self, fmt: str, *args: object) -> None:
        print(f"ERRO [{self.log_date_time_string()}] {fmt % args}")


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), SimulatorHandler)
    print(f"Simulador disponível em http://{HOST}:{PORT}")
    print("Acesso limitado a este computador. Pressione Ctrl+C para encerrar.")
    if HOST in ("127.0.0.1", "localhost"):
        webbrowser.open(f"http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
