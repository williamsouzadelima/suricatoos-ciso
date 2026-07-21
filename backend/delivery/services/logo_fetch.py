"""Busca do logo do cliente a partir do domínio.

Ordem (decisão do produto): site do PRÓPRIO cliente → Clearbit Logo API → favicon Google.
Reusa o SSRF-guard app-wide (core.net_safety.assert_public_url) e espelha o padrão de fetch
endurecido de doc_management._safe_url_fetcher (sem seguir redirect cego, cap de bytes).
Validação de imagem por magic-byte (python-magic) + Pillow — não confia no Content-Type remoto.
"""
import io
import logging
import re
from urllib.parse import urljoin, urlparse

import requests

from core.net_safety import assert_public_url, BlockedRequestError, DnsLookupError

logger = logging.getLogger(__name__)

_RASTER_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}
_ICO_TYPES = {"image/x-icon", "image/vnd.microsoft.icon"}
_MAX_IMG_BYTES = 5 * 1024 * 1024
_MAX_HTML_BYTES = 1 * 1024 * 1024
_TIMEOUT = 10
# UA de navegador real — muitos sites bloqueiam UA de bot (403). Sites atrás de
# Cloudflare/WAF ainda podem bloquear (challenge JS), aí caímos nos agregadores.
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$"
)


def normalize_domain(raw):
    """'https://www.Galapagos.com/x?y' -> 'galapagos.com'. '' se inválido."""
    if not raw:
        return ""
    raw = raw.strip().lower()
    if "://" not in raw:
        raw = "http://" + raw  # só p/ o urlparse extrair o host
    parsed = urlparse(raw)
    host = (parsed.hostname or "").strip()
    if host.startswith("www."):
        host = host[4:]
    return host if _DOMAIN_RE.match(host) else ""


def _safe_get(url, *, max_bytes, accept=None, max_redirects=3):
    """GET endurecido: valida cada hop com o SSRF-guard, não segue redirect cego,
    corta bytes. Retorna (bytes, content_type) ou (None, None)."""
    headers = {"User-Agent": _UA}
    if accept:
        headers["Accept"] = accept
    for _ in range(max_redirects + 1):
        try:
            assert_public_url(url, allowed_schemes=("https", "http"))
        except (BlockedRequestError, DnsLookupError, ValueError) as e:
            logger.debug("logo_fetch bloqueado/dns url=%s err=%s", url, e)
            return None, None
        r = None
        try:
            r = requests.get(
                url, timeout=_TIMEOUT, allow_redirects=False, stream=True, headers=headers
            )
            if 300 <= r.status_code < 400:
                loc = r.headers.get("Location")
                if not loc:
                    return None, None
                url = urljoin(url, loc)  # revalida no próximo loop (anti-SSRF)
                continue
            if r.status_code != 200:
                return None, None
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            content = r.raw.read(max_bytes + 1, decode_content=True)
            if not content or len(content) > max_bytes:
                return None, None
            return content, ctype
        except Exception as e:
            logger.debug("logo_fetch erro get url=%s err=%s", url, e)
            return None, None
        finally:
            if r is not None:
                r.close()
    return None, None  # redirects demais


def _validate_image(content, ctype):
    """Sniff por magic-byte + Pillow. ico -> png. Descarta svg/pdf/html/texto.
    Retorna (bytes, ext) ou None."""
    try:
        import magic

        real = magic.from_buffer(content[:2048], mime=True)
    except Exception:
        real = ctype
    real = (real or "").lower()

    if real in _ICO_TYPES:
        try:
            from PIL import Image

            im = Image.open(io.BytesIO(content)).convert("RGBA")
            buf = io.BytesIO()
            im.save(buf, format="PNG")
            return buf.getvalue(), "png"
        except Exception:
            return None

    if real not in _RASTER_EXT:
        return None  # svg/pdf/html/texto -> descarta (pptx não renderiza svg)

    try:
        from PIL import Image

        Image.open(io.BytesIO(content)).verify()
    except Exception:
        return None
    return content, _RASTER_EXT[real]


def _img_area(content):
    try:
        from PIL import Image

        w, h = Image.open(io.BytesIO(content)).size
        return w * h
    except Exception:
        return 0


def _from_site(domain):
    """Extrai o logo do próprio site do cliente (nenhum terceiro recebe o domínio).
    Usa só apple-touch-icon + favicon/icon (tiles de logo) — NÃO og:image, que
    costuma ser um banner social 1200x630, não o logo. Escolhe a MAIOR imagem válida."""
    html, _ = _safe_get(f"https://{domain}/", max_bytes=_MAX_HTML_BYTES, accept="text/html")
    if html is None:
        html, _ = _safe_get(f"http://{domain}/", max_bytes=_MAX_HTML_BYTES, accept="text/html")
    tags = []
    if html:
        head = html.decode("utf-8", "ignore")[:200000]
        tags += re.findall(
            r'<link[^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]*>', head, re.I
        )
        tags += re.findall(r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]*>', head, re.I)
    base = f"https://{domain}/"
    urls = []
    for tag in tags:
        m = re.search(r'(?:href|content)=["\']([^"\']+)["\']', tag, re.I)
        if m:
            urls.append(urljoin(base, m.group(1)))
    # caminhos convencionais
    urls.append(f"https://{domain}/apple-touch-icon.png")
    urls.append(f"https://{domain}/favicon.ico")
    seen, best = set(), None
    for u in urls:
        if u in seen or len(seen) >= 10:
            continue
        seen.add(u)
        content, ct = _safe_get(u, max_bytes=_MAX_IMG_BYTES, accept="image/*")
        if content is None:
            continue
        vi = _validate_image(content, ct)
        if not vi:
            continue
        area = _img_area(vi[0])
        if best is None or area > best[2]:
            best = (vi[0], vi[1], area)
    return (best[0], best[1], "site") if best else None


def _from_unavatar(domain):
    """Agregador de logo (unavatar.io) — substitui a Clearbit Logo API (descontinuada).
    `fallback=false` faz retornar 404 quando não há logo real (evita placeholder genérico)."""
    content, ct = _safe_get(
        f"https://unavatar.io/{domain}?fallback=false",
        max_bytes=_MAX_IMG_BYTES,
        accept="image/*",
    )
    if content is None:
        return None
    vi = _validate_image(content, ct)
    return (vi[0], vi[1], "unavatar") if vi else None


def _from_google(domain):
    content, ct = _safe_get(
        f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
        max_bytes=_MAX_IMG_BYTES,
        accept="image/*",
    )
    if content is None:
        return None
    vi = _validate_image(content, ct)
    return (vi[0], vi[1], "google") if vi else None


def fetch_client_logo(domain):
    """Retorna (bytes, ext, source) do 1º sucesso na ordem site→clearbit→google, ou None."""
    norm = normalize_domain(domain)
    if not norm:
        return None
    for fn in (_from_site, _from_unavatar, _from_google):
        try:
            res = fn(norm)
        except Exception as e:
            logger.debug("logo_fetch fonte %s erro: %s", fn.__name__, e)
            res = None
        if res:
            return res
    return None
