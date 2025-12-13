import asyncio, re, pathlib, json, hashlib, platform, socket, argparse, os
from datetime import datetime
from playwright.async_api import async_playwright
from collections import Counter

# ============================================================================
# KONFIGURATION
# ============================================================================

# === Chrome-Profil automatisch erkennen (plattformunabhängig) ===
def get_default_chrome_profile():
    """Ermittelt den Chrome-Profil-Pfad basierend auf dem Betriebssystem"""
    system = platform.system()
    
    if system == 'Windows':
        # Windows: Standardmäßig "Default" Profil, aber konfigurierbar
        base = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        # Für andere Profile: ändere "Default" zu "Profile 1", "Profile 2", etc.
        return os.path.join(base, "Profile 1")
    
    elif system == 'Darwin':  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
    
    elif system == 'Linux':
        return os.path.expanduser("~/.config/google-chrome/Default")
    
    else:
        raise OSError(f"Nicht unterstütztes Betriebssystem: {system}")

# Chrome-Profil-Pfad
# Option 1: Automatisch erkennen
USER_DATA_DIR = get_default_chrome_profile()

# Option 2: Manuell setzen (auskommentiert)
# USER_DATA_DIR = r"C:\Users\post\AppData\Local\Google\Chrome\User Data\Profile 1"  # Windows
# USER_DATA_DIR = "/Users/USERNAME/Library/Application Support/Google/Chrome/Default"  # macOS
# USER_DATA_DIR = "/home/USERNAME/.config/google-chrome/Default"  # Linux

# === Zusätzliche Backup-Orte (optional - leer lassen wenn nicht gewünscht) ===
BACKUP_LOCATIONS = [
    # Hier kannst du optional weitere Pfade eintragen:
    # r"D:\Backups\ChatGPT",
    # r"E:\USB_Stick\ChatGPT",
]

# === Erweiterte Features ===
SAVE_SCREENSHOTS = True
SAVE_RAW_HTML = True
SAVE_METADATA = True  # Jetzt IMMER für alle Chats

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def slug(s: str) -> str:
    """Bereinigt String für Dateinamen"""
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"[^-\w]", "", s, flags=re.UNICODE)
    return s.lower()[:120] or "chat"

def extract_auto_keywords(text: str, num_keywords: int = 5) -> list:
    """
    Extrahiert automatisch Keywords aus Text.
    Verwendet eine Kombination aus:
    - Häufigkeitsanalyse
    - Filterung von Stopwörtern
    - Erkennung von Eigennamen (Großschreibung)
    - Technischen Begriffen
    """
    
    # Deutsche und englische Stopwörter
    stopwords = {
        # Deutsch
        'der', 'die', 'das', 'und', 'oder', 'aber', 'ist', 'sind', 'war', 'waren',
        'ein', 'eine', 'einer', 'einem', 'einen', 'ich', 'du', 'er', 'sie', 'es',
        'wir', 'ihr', 'mit', 'von', 'zu', 'auf', 'für', 'nicht', 'auch', 'wenn',
        'dass', 'als', 'wie', 'bei', 'nach', 'über', 'nur', 'noch', 'dann', 'kann',
        'was', 'hat', 'haben', 'wird', 'werden', 'können', 'sollte', 'würde', 'hier',
        'dort', 'jetzt', 'dann', 'mehr', 'sehr', 'ganz', 'immer', 'alle', 'meine',
        'deine', 'seine', 'ihre', 'diese', 'dieses', 'dieser', 'welche', 'welches',
        'welcher', 'bitte', 'danke', 'ja', 'nein', 'okay', 'ok',
        # English
        'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'a', 'an', 'i',
        'you', 'he', 'she', 'it', 'we', 'they', 'with', 'from', 'to', 'for',
        'not', 'also', 'if', 'that', 'as', 'like', 'at', 'after', 'about', 'only',
        'can', 'will', 'would', 'should', 'could', 'has', 'have', 'had', 'do',
        'does', 'did', 'be', 'been', 'being', 'here', 'there', 'now', 'then',
        'more', 'very', 'all', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'this', 'that', 'these', 'those', 'which', 'what', 'please', 'thanks',
        'yes', 'no', 'okay', 'ok'
    }
    
    # Text vorverarbeiten
    text_lower = text.lower()
    
    # Wörter extrahieren (mindestens 3 Zeichen)
    words = re.findall(r'\b[a-zäöüß]{3,}\b', text_lower)
    
    # Eigennamen finden (Großbuchstaben am Anfang, nicht am Satzanfang)
    proper_nouns = re.findall(r'(?<!^)(?<!\. )\b([A-ZÄÖÜ][a-zäöüß]{2,})\b', text)
    proper_nouns_lower = [w.lower() for w in proper_nouns]
    
    # Technische Begriffe / Akronyme (2+ Großbuchstaben)
    acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
    acronyms_lower = [w.lower() for w in acronyms]
    
    # Zahlen mit Einheiten (z.B. "20kg", "5cm")
    units = re.findall(r'\b\d+\s*(?:kg|g|cm|m|km|mm|ml|l|°c|grad|prozent|%)\b', text_lower)
    
    # Häufigkeit zählen (ohne Stopwörter)
    word_freq = Counter([w for w in words if w not in stopwords and len(w) > 3])
    
    # Bonus für Eigennamen und Akronyme
    for word in proper_nouns_lower:
        if word not in stopwords:
            word_freq[word] += 5
    
    for word in acronyms_lower:
        if word not in stopwords:
            word_freq[word] += 3
    
    # Keywords sammeln
    keywords = []
    
    # Top Akronyme (max 2)
    for acronym in acronyms[:2]:
        if acronym not in keywords:
            keywords.append(acronym)
    
    # Top Eigennamen (max 3)
    proper_freq = Counter(proper_nouns_lower)
    for word, _ in proper_freq.most_common(3):
        # Original-Schreibweise finden
        for pn in proper_nouns:
            if pn.lower() == word:
                if pn not in keywords and len(keywords) < num_keywords:
                    keywords.append(pn)
                break
    
    # Top häufige Wörter auffüllen
    for word, freq in word_freq.most_common(20):
        if len(keywords) >= num_keywords:
            break
        if word not in [k.lower() for k in keywords]:
            # Mindestens 2x vorkommen
            if freq >= 2:
                keywords.append(word.capitalize())
    
    return keywords[:num_keywords]

def as_markdown(turns):
    """Konvertiert Chat-Turns zu Markdown"""
    lines = []
    for t in turns:
        who = "User" if t["role"] == "user" else "Assistant"
        lines.append(f"### {who}\n")
        lines.append(t["text"])
        lines.append("")
    return "\n".join(lines)

def save_system_info(outdir):
    """Speichert System-Informationen für Dokumentation"""
    info = {
        "export_timestamp": datetime.now().isoformat(),
        "system": platform.system(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "chrome_profile": USER_DATA_DIR,
        "export_tool": "Playwright Python Script (Enhanced v2)",
        "account_type": "ChatGPT Business Account",
        "note": "Export für Dokumentationszwecke - Account-Tracking-Untersuchung"
    }
    
    info_path = outdir / "export_info.json"
    info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"System-Info gespeichert: {info_path.name}")
    return info

def create_directory_structure(base_path):
    """Erstellt Ordnerstruktur für Export"""
    base_path.mkdir(exist_ok=True)
    
    subdirs = {
        'markdown': base_path / "markdown",
        'pdf': base_path / "pdf",
        'metadata': base_path / "metadata",
    }
    
    if SAVE_SCREENSHOTS:
        subdirs['screenshots'] = base_path / "screenshots"
    if SAVE_RAW_HTML:
        subdirs['raw_html'] = base_path / "raw_html"
    
    for subdir in subdirs.values():
        subdir.mkdir(exist_ok=True)
    
    return subdirs

async def save_chat_metadata(page, chat_title, timestamp, content, dirs, project_name=None, keywords=None):
    """Speichert Metadaten für einen Chat - IMMER"""
    
    # Automatische Keywords aus Inhalt extrahieren
    auto_keywords = extract_auto_keywords(content, num_keywords=5)
    
    meta = {
        "export_timestamp": datetime.now().isoformat(),
        "chat_timestamp": timestamp,
        "chat_url": page.url,
        "chat_title": chat_title,
        "project": project_name or "None",
        "user_agent": await page.evaluate("navigator.userAgent"),
        "account_info": "ChatGPT Business Account",
        "sha256_markdown": hashlib.sha256(content.encode()).hexdigest(),
        "browser": "Chrome",
        "auto_keywords": auto_keywords,  # Automatisch erkannte Keywords
    }
    
    # Prüfe auf manuelle Keywords (nur wenn welche angegeben wurden)
    if keywords:
        meta["manual_keywords_searched"] = keywords
        meta["manual_keywords_found"] = []
        content_lower = content.lower()
        for keyword in keywords:
            if keyword.lower() in content_lower:
                meta["manual_keywords_found"].append(keyword)
    
    meta_path = dirs['metadata'] / f"{chat_title}-{timestamp}.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
    return meta

async def save_screenshots_for_chat(page, chat_title, timestamp, dirs, keywords=None):
    """Speichert Screenshots"""
    if not SAVE_SCREENSHOTS:
        return []
    
    screenshot_paths = []
    
    # Vollbild-Screenshot
    try:
        full_path = dirs['screenshots'] / f"{chat_title}-{timestamp}-full.png"
        await page.screenshot(path=str(full_path), full_page=True)
        screenshot_paths.append(full_path)
    except Exception as e:
        print(f"  Vollbild-Screenshot fehlgeschlagen: {e}")
    
    # Keyword-Screenshots (nur wenn Keywords angegeben wurden)
    # WICHTIG: Nur im Main-Content suchen, nicht in Sidebar/UI
    if keywords:
        for keyword in keywords:
            try:
                # Suche nur im Main-Content-Bereich
                locator = page.locator(f"main >> text={keyword}")
                count = await locator.count()
                if count > 0:
                    print(f"  Keyword '{keyword}' gefunden im Chat-Content!")
                    element = locator.first
                    kw_path = dirs['screenshots'] / f"{chat_title}-{timestamp}-keyword-{slug(keyword)}.png"
                    await element.screenshot(path=str(kw_path))
                    screenshot_paths.append(kw_path)
                    print(f"     Screenshot gespeichert: {kw_path.name}")
            except Exception:
                pass
    
    return screenshot_paths

async def save_raw_html(page, chat_title, timestamp, dirs):
    """Speichert HTML-Quellcode"""
    if not SAVE_RAW_HTML:
        return None
    
    try:
        html_content = await page.content()
        html_path = dirs['raw_html'] / f"{chat_title}-{timestamp}.html"
        html_path.write_text(html_content, encoding='utf-8')
        return html_path
    except Exception as e:
        print(f"  HTML-Speicherung fehlgeschlagen: {e}")
        return None

def copy_to_backup_locations(source_dir):
    """Kopiert Export zu zusätzlichen Backup-Orten"""
    if not BACKUP_LOCATIONS:
        return
    
    import shutil
    
    print("\n" + "="*60)
    print("Erstelle Backups...")
    print("="*60)
    
    for backup_path in BACKUP_LOCATIONS:
        try:
            backup_path = pathlib.Path(backup_path)
            target = backup_path / source_dir.name
            
            if not backup_path.exists():
                print(f"Backup-Pfad existiert nicht: {backup_path}")
                print(f"Soll er erstellt werden? (j/n)")
                response = input().strip().lower()
                if response == 'j':
                    backup_path.mkdir(parents=True, exist_ok=True)
                else:
                    continue
            
            print(f"Kopiere nach: {target}")
            shutil.copytree(source_dir, target, dirs_exist_ok=True)
            print(f"Backup erfolgreich: {target}")
            
        except Exception as e:
            print(f"Backup fehlgeschlagen für {backup_path}: {e}")
    
    print("="*60)

async def extract_turns(page):
    """Extrahiert Chat-Nachrichten - VERBESSERTE VERSION"""
    await page.wait_for_selector("main", timeout=15000)
    
    # Mehrere Selektoren probieren
    selectors = [
        'main [data-testid="conversation-turn"]',
        'main [data-message-author-role]',
        'main article',
        'main div[class*="group"]',  # Neue ChatGPT UI
    ]
    
    elements = None
    for selector in selectors:
        elements = await page.locator(selector).all()
        if elements and len(elements) > 0:
            print(f"  Turns gefunden mit Selektor: {selector} ({len(elements)} Elemente)")
            break
    
    if not elements:
        print("  WARNUNG: Keine Chat-Elemente gefunden!")
        return []
    
    turns = []
    for el in elements:
        try:
            # Rolle ermitteln
            role_attr = await el.get_attribute("data-message-author-role")
            if not role_attr:
                # Fallback: Prüfe Klassen oder Text
                classes = await el.get_attribute("class") or ""
                if "user" in classes.lower():
                    role_attr = "user"
                elif "assistant" in classes.lower():
                    role_attr = "assistant"
            
            # Text extrahieren
            txt = await el.inner_text()
            txt = txt.strip()
            
            if txt and role_attr:
                turns.append({"role": role_attr, "text": txt})
            elif txt:
                # Fallback: Wenn keine Rolle, nimm abwechselnd user/assistant
                role = "user" if len(turns) % 2 == 0 else "assistant"
                turns.append({"role": role, "text": txt})
        except Exception as e:
            print(f"  Fehler beim Extrahieren eines Elements: {e}")
            continue
    
    return turns

# ============================================================================
# SIDEBAR & NAVIGATION
# ============================================================================

SIDEBAR_SELECTORS = [
    '[data-testid="conversation-list"]',
    'nav a[href*="/c/"]',
    'aside a[href*="/c/"]',
    'div[class*="sidebar"] a[href*="/c/"]',
]

async def wait_for_sidebar(page, timeout_ms=120000):
    """Wartet auf Sidebar"""
    end = asyncio.get_event_loop().time() + (timeout_ms / 1000)
    while asyncio.get_event_loop().time() < end:
        for sel in SIDEBAR_SELECTORS:
            if await page.locator(sel).count() > 0:
                return True
        await asyncio.sleep(1.0)
    return False

async def navigate_to_project(page, project_name):
    """Navigiert zu einem bestimmten Projekt"""
    print(f"\nNavigiere zu Projekt: {project_name}")
    
    # Aktuelle URL merken
    url_before = page.url
    print(f"  URL vorher: {url_before}")
    
    # Warte kurz für Projektliste
    await asyncio.sleep(2.0)
    
    # Suche nach Projekt-Link in der Sidebar
    project_selectors = [
        f'nav a:has-text("{project_name}")',
        f'aside a:has-text("{project_name}")',
        f'[data-testid="project-list"] a:has-text("{project_name}")',
        f'div[class*="project"] a:has-text("{project_name}")',
    ]
    
    for selector in project_selectors:
        try:
            locator = page.locator(selector)
            count = await locator.count()
            if count > 0:
                print(f"  Projekt gefunden mit Selektor: {selector}")
                await locator.first.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(3.0)  # Mehr Zeit für Projekt-Chats laden
                
                # Prüfe ob URL sich geändert hat
                url_after = page.url
                print(f"  URL nachher: {url_after}")
                
                if url_after != url_before:
                    print(f"  -> Erfolgreich zu Projekt navigiert")
                    return True
                else:
                    print(f"  -> URL unverändert, versuche nächsten Selektor...")
                    continue
                    
        except Exception as e:
            print(f"  Fehler mit Selektor {selector}: {e}")
            continue
    
    print(f"  FEHLER: Projekt '{project_name}' nicht gefunden!")
    return False

async def get_chat_links(page, in_project=False, export_all=False):
    """Holt Chat-Links - jetzt mit Projekt-Unterscheidung"""
    
    # Alle Chat-Links holen
    all_links = await page.locator('a[href*="/c/"]').all()
    
    if not all_links:
        print("  WARNUNG: Keine Chat-Links gefunden!")
        return []
    
    print(f"  Gesamt gefundene Links: {len(all_links)}")
    
    if export_all:
        # --all Modus: KEINE Filterung, alle Links zurückgeben
        print("  Modus --all: Exportiere ALLE Chats (Projekte + Normale)")
        return all_links
    
    elif in_project:
        # Im Projekt: Nur Links die "/g/g-p-" in der URL haben
        print("  Filtere nach Projekt-Chats (URL enthält '/g/g-p-')...")
        project_links = []
        
        for link in all_links:
            href = await link.get_attribute("href")
            if href and "/g/g-p-" in href:
                project_links.append(link)
        
        print(f"  Projekt-Chat-Links gefunden: {len(project_links)} Stück")
        return project_links
    
    else:
        # Außerhalb von Projekten: Nur Links die NICHT "/g/g-p-" haben
        print("  Filtere nach normalen Chats (URL ohne '/g/g-p-')...")
        normal_links = []
        
        for link in all_links:
            href = await link.get_attribute("href")
            if href and "/g/g-p-" not in href:
                normal_links.append(link)
        
        print(f"  Normale Chat-Links gefunden: {len(normal_links)} Stück")
        return normal_links

async def export_chat_list(page, chat_links, dirs, project_name, keywords, filter_keywords):
    """Exportiert eine Liste von Chats"""
    if not chat_links:
        print("Keine Chats zum Exportieren.")
        return 0
    
    # URLs aus Links extrahieren (bevor DOM sich ändert)
    chat_urls = []
    for link in chat_links:
        href = await link.get_attribute("href")
        if href:
            # Relative URLs zu absoluten machen
            if href.startswith('/'):
                href = f"https://chatgpt.com{href}"
            chat_urls.append(href)
    
    print(f"Chat-URLs extrahiert: {len(chat_urls)}")
    
    seen_urls = set()
    exported_count = 0
    skipped_count = 0
    
    for i, url in enumerate(chat_urls):
        if url in seen_urls:
            continue
        
        print(f"\n[{i+1}/{len(chat_urls)}] Öffne Chat: {url.split('/')[-1][:20]}...")
        
        try:
            # Direkt zur URL navigieren
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(2.0)
            
            # Filter-Check: Wenn filter_keywords gesetzt, erst Inhalt prüfen
            if filter_keywords:
                turns = await extract_turns(page)
                if not turns:
                    print(f"  -> Kein Inhalt, überspringe...")
                    skipped_count += 1
                    continue
                
                # Markdown erstellen für Filter-Check
                md_content = as_markdown(turns)
                content_lower = md_content.lower()
                
                # Prüfen ob mindestens ein Filter-Keyword enthalten ist
                has_keyword = False
                for filter_kw in filter_keywords:
                    if filter_kw.lower() in content_lower:
                        has_keyword = True
                        break
                
                if not has_keyword:
                    print(f"  -> Filter-Keywords nicht gefunden, überspringe...")
                    skipped_count += 1
                    continue
            
            # Export durchführen
            success = await export_chat(page, dirs, project_name, keywords)
            
            if success:
                exported_count += 1
                seen_urls.add(url)
        
        except Exception as e:
            print(f"  FEHLER beim Exportieren: {e}")
            continue
    
    if filter_keywords and skipped_count > 0:
        print(f"\n  Übersprungen (Filter): {skipped_count} Chats")
    
    return exported_count

# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

async def export_chat(page, dirs, project_name=None, keywords=None):
    """Exportiert einen einzelnen Chat mit allen Features"""
    
    # Warte auf Content
    await page.wait_for_load_state("domcontentloaded")
    await asyncio.sleep(2.0)  # Mehr Zeit für Rendering
    
    title = slug(await page.title())
    
    # Turns extrahieren
    turns = await extract_turns(page)
    
    if not turns or len(turns) == 0:
        print(f"  -> Kein Inhalt erkannt in '{title}', überspringe...")
        return False
    
    ts = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    
    # Bei Projekt-Chats: Unterordner erstellen
    actual_dirs = dirs
    if project_name:
        project_slug = slug(project_name)
        actual_dirs = {}
        for key, base_dir in dirs.items():
            project_dir = base_dir / project_slug
            project_dir.mkdir(exist_ok=True)
            actual_dirs[key] = project_dir
    
    # Markdown speichern
    md_content = as_markdown(turns)
    md_path = actual_dirs['markdown'] / f"{title}-{ts}.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"  Markdown: {md_path.name}")
    
    # PDF speichern
    try:
        pdf_path = actual_dirs['pdf'] / f"{title}-{ts}.pdf"
        await page.pdf(path=str(pdf_path), format="A4", print_background=True)
        print(f"  PDF: {pdf_path.name}")
    except Exception as e:
        print(f"  PDF nicht möglich: {e}")
    
    # Metadaten IMMER speichern
    meta = await save_chat_metadata(page, title, ts, md_content, actual_dirs, project_name, keywords)
    
    # Auto-Keywords immer ausgeben
    if meta.get("auto_keywords"):
        print(f"  Auto-Keywords: {', '.join(meta['auto_keywords'])}")
    
    # Manuelle Keyword-Ausgabe nur wenn Keywords angegeben wurden
    if keywords:
        if meta.get("manual_keywords_found"):
            print(f"  Manuelle Keywords gefunden: {', '.join(meta['manual_keywords_found'])}")
        else:
            print(f"  Keine manuellen Keywords gefunden (gesucht: {', '.join(keywords)})")
    
    # Screenshots
    if SAVE_SCREENSHOTS:
        screenshots = await save_screenshots_for_chat(page, title, ts, actual_dirs, keywords)
        if screenshots:
            print(f"  Screenshots: {len(screenshots)}")
    
    # HTML
    if SAVE_RAW_HTML:
        html = await save_raw_html(page, title, ts, actual_dirs)
        if html:
            print(f"  HTML: {html.name}")
    
    return True

async def run(project_name=None, export_all=False, keywords=None, filter_keywords=None):
    """Hauptfunktion mit Projektunterstützung"""
    
    # Dynamischen Exportordner-Namen erstellen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_name_parts = ["chatgpt_business_export"]
    
    if project_name:
        # Projekt-Name bereinigen für Dateinamen
        clean_project = slug(project_name)
        export_name_parts.append(f"project_{clean_project}")
    
    if keywords:
        # Keywords zu einem String zusammenfassen
        keywords_str = "_".join([slug(kw) for kw in keywords[:3]])  # Max 3 Keywords
        export_name_parts.append(f"kw_{keywords_str}")
    
    export_name_parts.append(timestamp)
    export_dir = pathlib.Path("_".join(export_name_parts))
    
    # Erstelle Ordnerstruktur
    dirs = create_directory_structure(export_dir)
    save_system_info(export_dir)
    
    print("\n" + "="*60)
    print(f"Export-Verzeichnis: {export_dir.absolute()}")
    print("="*60)
    
    if export_all:
        print("Modus: ALLE Chats (auch in Projekten)")
    elif project_name:
        print(f"Modus: Nur Projekt '{project_name}'")
    else:
        print("Modus: Nur Chats außerhalb von Projekten")
    
    print(f"Screenshots: {'✓' if SAVE_SCREENSHOTS else '✗'}")
    print(f"Raw HTML: {'✓' if SAVE_RAW_HTML else '✗'}")
    print(f"Metadaten: IMMER")
    
    if keywords:
        print(f"Keywords (Tagging): {', '.join(keywords)}")
    
    if filter_keywords:
        print(f"Filter (nur Chats mit): {', '.join(filter_keywords)}")
    
    if BACKUP_LOCATIONS:
        print(f"Backup-Orte: {len(BACKUP_LOCATIONS)} konfiguriert")
    print("="*60 + "\n")
    
    async with async_playwright() as pw:
        print(f"Erkanntes Betriebssystem: {platform.system()}")
        print(f"Chrome-Profil: {USER_DATA_DIR}")
        print("Starte echtes Chrome-Profil...")
        ctx = await pw.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--no-first-run",
                "--no-default-browser-check"
            ]
        )
        from playwright._impl._errors import TargetClosedError
        
        page = await ctx.new_page()
        
        # WebDriver-Flag entfernen
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        try:
            await page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=30000)
        except TargetClosedError:
            page = await ctx.new_page()
            await page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Seite konnte nicht geladen werden: {e}")
        
        await asyncio.sleep(3.0)
        
        print("\n" + "="*60)
        print("WICHTIG: Falls du noch nicht eingeloggt bist:")
        print("   1. Logge dich jetzt MANUELL im geöffneten Chrome ein")
        print("   2. Löse das Cloudflare-CAPTCHA falls nötig")
        print("   3. Warte bis die Chatliste links sichtbar ist")
        print("   4. Dann drücke hier ENTER um fortzufahren")
        print("="*60)
        input("\nENTER drücken wenn eingeloggt und Chatliste sichtbar ist... ")
        
        print("\nWarte auf Sidebar...")
        ok = await wait_for_sidebar(page, timeout_ms=60000)
        if not ok:
            print("Sidebar nicht automatisch gefunden.")
            input("Bitte Chatliste sichtbar machen, dann ENTER...")
        
        # Projektmodus?
        projects_to_process = []
        
        if export_all:
            # --all: Erst alle Projekt-Namen sammeln
            print("\nSuche alle verfügbaren Projekte...")
            project_elements = await page.locator('nav a[href*="/g/g-p-"], aside a[href*="/g/g-p-"]').all()
            
            seen_projects = set()
            for elem in project_elements:
                href = await elem.get_attribute("href")
                if href and "/g/g-p-" in href:
                    # Projekt-Name aus Href extrahieren
                    try:
                        text = await elem.inner_text()
                        if text and text not in seen_projects:
                            projects_to_process.append(text.strip())
                            seen_projects.add(text)
                    except:
                        pass
            
            print(f"Gefundene Projekte: {len(projects_to_process)}")
            for proj in projects_to_process:
                print(f"  - {proj}")
        
        elif project_name:
            # Nur ein spezifisches Projekt
            projects_to_process.append(project_name)
        
        # Phase 1: Normale Chats (nur wenn nicht --project einzelnes Projekt)
        exported_count = 0
        
        if not project_name or export_all:
            print("\n" + "="*60)
            print("PHASE 1: Exportiere normale Chats (außerhalb von Projekten)")
            print("="*60)
            
            chat_links = await get_chat_links(page, in_project=False, export_all=False)
            print(f"Gefundene normale Chats: {len(chat_links)}")
            
            exported_count += await export_chat_list(page, chat_links, dirs, None, keywords, filter_keywords)
        
        # Phase 2: Projekt-Chats
        if projects_to_process:
            print("\n" + "="*60)
            print(f"PHASE 2: Exportiere Chats aus {len(projects_to_process)} Projekt(en)")
            print("="*60)
            
            for proj_name in projects_to_process:
                print(f"\n>>> Projekt: {proj_name}")
                
                success = await navigate_to_project(page, proj_name)
                if not success:
                    print(f"Überspringe Projekt '{proj_name}' - Navigation fehlgeschlagen")
                    continue
                
                chat_links = await get_chat_links(page, in_project=True, export_all=False)
                print(f"Gefundene Chats in Projekt '{proj_name}': {len(chat_links)}")
                
                exported_count += await export_chat_list(page, chat_links, dirs, proj_name, keywords, filter_keywords)
                
                # Zurück zur Hauptseite
                await page.goto("https://chatgpt.com/", wait_until="domcontentloaded")
                await asyncio.sleep(2.0)
        
        print("\n" + "="*60)
        print(f"Fertig! {exported_count} Chats exportiert")
        print(f"Speicherort: {export_dir.absolute()}")
        print("="*60)
        
        # Backup
        if BACKUP_LOCATIONS:
            copy_to_backup_locations(export_dir)
        
        input("\nENTER zum Schließen...")
        await ctx.close()

# ============================================================================
# CLI-INTERFACE
# ============================================================================

def main():
    try:
        parser = argparse.ArgumentParser(
            description="ChatGPT Business Account Export mit Projekt-Support",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Beispiele:
  python export_enhanced_v2.py                              # Nur Chats außerhalb von Projekten
  python export_enhanced_v2.py --project "MyWork"           # Nur Chats im Projekt "MyWork"
  python export_enhanced_v2.py --all                        # ALLE Chats inkl. Projekte
  python export_enhanced_v2.py --keywords NRW OWL           # Keywords für Tagging/Screenshots
  python export_enhanced_v2.py --filter-keywords MCP        # NUR Chats die "MCP" enthalten
  python export_enhanced_v2.py --all --filter-keywords MCP  # Alle Chats mit "MCP"
        """
        )
        
        parser.add_argument(
            '--project',
            type=str,
            help='Exportiere nur Chats aus diesem Projekt'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Exportiere ALLE Chats (auch in Projekten)'
        )
        
        parser.add_argument(
            '--keywords',
            nargs='+',
            help='Keywords für Screenshots und Tagging (z.B. --keywords NRW "Bad Sassendorf")'
        )
        
        parser.add_argument(
            '--filter-keywords',
            nargs='+',
            help='Exportiere NUR Chats die diese Keywords enthalten (z.B. --filter-keywords MCP)'
        )
        
        args = parser.parse_args()
        
        asyncio.run(run(
            project_name=args.project, 
            export_all=args.all, 
            keywords=args.keywords,
            filter_keywords=args.filter_keywords
        ))
        
    except Exception as e:
        print("\n" + "="*60)
        print("FEHLER:")
        print("="*60)
        print(f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        input("\nENTER zum Schließen...")
        raise

if __name__ == "__main__":
    main()
