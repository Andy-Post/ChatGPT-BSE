# ChatGPT Plus/Business Export Tool

Python-Script zum automatisierten Export von ChatGPT Business Account Conversations mit Unterstützung für Projekte, Metadaten, automatischer Keyword-Extraktion und flexibler Filterung.

## Features

- **Projekt-Support**: Exportiere Chats aus spezifischen Projekten oder alle Chats
- **Automatische Keyword-Extraktion**: KI-gestützte Erkennung von 3-5 relevanten Keywords pro Chat
- **Flexible Filterung**: Exportiere nur Chats die bestimmte Keywords enthalten
- **Vollständige Metadaten**: SHA256-Hash, Timestamps, URLs, Auto-Keywords für jeden Chat
- **Multiple Formate**: Markdown, PDF, HTML-Rohdaten
- **Screenshots**: Vollbild-Screenshots und gezielte Keyword-Screenshots
- **Manuelle Keyword-Suche**: Durchsuche Chats nach spezifischen Begriffen
- **Projekt-Ordnerstruktur**: Automatische Unterordner pro Projekt
- **Backup-Unterstützung**: Automatisches Kopieren zu konfigurierten Backup-Orten
- **Plattform-unabhängig**: Funktioniert auf Windows, macOS und Linux
- **Account-Tracking**: Dokumentation für GDPR-Untersuchungen

## Voraussetzungen

- Python 3.8+
- Google Chrome (funktioniert auf Windows, macOS, Linux)
- Playwright für Python

## Unterstützte Betriebssysteme

- Windows 10/11
- macOS (Intel & Apple Silicon)
- Linux (Ubuntu, Debian, Fedora, etc.)

## Installation

1. Repository klonen:
```bash
git clone https://github.com/Andy-Post/ChatGPT-BSE.git
cd ChatGPT-BSE
```

2. Dependencies installieren:
```bash
pip install playwright
playwright install chrome
```

3. Chrome-Profil-Pfad konfigurieren (optional):

Das Script erkennt automatisch den Standard-Chrome-Profil-Pfad für dein Betriebssystem:
- **Windows**: `%LOCALAPPDATA%\Google\Chrome\User Data\Profile 1`
- **macOS**: `~/Library/Application Support/Google/Chrome/Default`
- **Linux**: `~/.config/google-chrome/Default`

Falls du ein anderes Chrome-Profil verwenden möchtest, öffne `export_enhanced_v2.py` und passe in den Zeilen 28-32 an.

4. **Wichtig**: Chrome muss vor dem Start komplett geschlossen sein!

## Verwendung

### Basis-Export (nur Chats außerhalb von Projekten)
```bash
python export_enhanced.py
```

### Export aus einem spezifischen Projekt
```bash
python export_enhanced.py --project "Projektname"
```

### Export aller Chats (inkl. Projekte)
```bash
python export_enhanced.py --all
```

### Export mit Keyword-Filter (nur Chats die Keywords enthalten)
```bash
python export_enhanced.py --all --filter-keywords "MCP" "Bitwig"
# Exportiert NUR Chats die "MCP" ODER "Bitwig" enthalten
```

### Mit manueller Keyword-Suche (für Tagging/Screenshots)
```bash
python export_enhanced.py --all --keywords "NRW" "Bad Sassendorf"
# Exportiert ALLE Chats, taggt die mit Keywords, macht Screenshots
```

### Kombiniert: Filter + Tagging
```bash
python export_enhanced.py --all --filter-keywords "MCP" --keywords "OSC" "Bitwig"
# Exportiert nur Chats mit "MCP", taggt diese zusätzlich mit "OSC"/"Bitwig"
```

## Ausgabestruktur

Das Script erstellt folgende Ordnerstruktur mit Projekt-Unterordnern:

```
chatgpt_business_export_project_mcp_20251213_155623/
├── markdown/
│   ├── mcp/              # Chats aus Projekt "MCP"
│   │   └── chat-title.md
│   ├── natalie/          # Chats aus Projekt "Natalie"  
│   │   └── chat-title.md
│   └── chat-title.md     # Normale Chats (ohne Projekt)
├── pdf/
│   ├── mcp/
│   └── natalie/
├── metadata/
│   ├── mcp/
│   │   └── chat-title.json
│   └── natalie/
├── screenshots/
│   ├── mcp/
│   └── natalie/
├── raw_html/
│   ├── mcp/
│   └── natalie/
└── export_info.json      # System-Informationen
```

### Verzeichnisname

Der Exportordner wird automatisch benannt:
- Basis: `chatgpt_business_export_YYYYMMDD_HHMMSS`
- Mit Projekt: `chatgpt_business_export_project_NAME_YYYYMMDD_HHMMSS`
- Mit Filter-Keywords: `chatgpt_business_export_kw_KEYWORD1_KEYWORD2_YYYYMMDD_HHMMSS`
- Kombiniert: `chatgpt_business_export_project_mcp_kw_nrw_owl_YYYYMMDD_HHMMSS`

## Metadaten-Format

Jeder Chat erhält eine JSON-Metadatendatei mit automatischer Keyword-Extraktion:

```json
{
  "export_timestamp": "2025-12-13T15:56:23",
  "chat_timestamp": "2025-12-13T15-56-23",
  "chat_url": "https://chatgpt.com/g/g-p-xxx/c/abc123",
  "chat_title": "beispiel-chat",
  "project": "MCP",
  "user_agent": "Mozilla/5.0...",
  "account_info": "ChatGPT Business Account",
  "sha256_markdown": "a1b2c3...",
  "browser": "Chrome",
  "auto_keywords": ["MCP", "Bitwig", "Automation", "Parameter", "OSC"],
  "manual_keywords_searched": ["NRW"],
  "manual_keywords_found": []
}
```

### Automatische Keywords

Das Script extrahiert automatisch 3-5 relevante Keywords aus jedem Chat:
- **Akronyme** (z.B. "MCP", "API", "OSC") - Bonus-Gewichtung
- **Eigennamen** (z.B. "Bitwig", "Playwright") - Bonus-Gewichtung  
- **Häufige Begriffe** (min. 2x vorkommend, gefiltert durch Stopwörter)
- Deutsch & Englisch unterstützt

## Konfiguration

### Chrome-Profil (automatisch erkannt)

Das Script erkennt automatisch den Standard-Chrome-Pfad für dein System.
Falls du ein anderes Profil verwenden möchtest, passe die Zeilen 28-32 in `export_enhanced_v2.py` an:

**Windows:**
```python
USER_DATA_DIR = r"C:\Users\USERNAME\AppData\Local\Google\Chrome\User Data\Profile 2"
```

**macOS:**
```python
USER_DATA_DIR = "/Users/USERNAME/Library/Application Support/Google/Chrome/Profile 1"
```

**Linux:**
```python
USER_DATA_DIR = "/home/USERNAME/.config/google-chrome/Profile 1"
```

### Backup-Orte (optional)
```python
BACKUP_LOCATIONS = [
    r"D:\Backups\ChatGPT",           # Windows
    "/Volumes/USB/ChatGPT",          # macOS
    "/media/usb/ChatGPT",            # Linux
]
```

### Features ein-/ausschalten
```python
SAVE_SCREENSHOTS = True
SAVE_RAW_HTML = True
```

## CLI-Optionen

| Option | Beschreibung |
|--------|-------------|
| `--project "Name"` | Exportiere nur Chats aus diesem Projekt |
| `--all` | Exportiere alle Chats inkl. Projekte |
| `--filter-keywords WORD1 WORD2` | Exportiere NUR Chats die diese Keywords enthalten |
| `--keywords WORD1 WORD2` | Keywords für Tagging und gezielte Screenshots |

### Unterschied: `--filter-keywords` vs `--keywords`

**`--filter-keywords`** (Filter-Modus):
- Exportiert **NUR** Chats die mindestens ein Keyword enthalten
- Überspringt alle anderen Chats
- Nutzen: Reduzierte Export-Menge, nur relevante Chats

**`--keywords`** (Tagging-Modus):
- Exportiert **ALLE** Chats
- Sucht Keywords in jedem Chat
- Macht Screenshots von Keyword-Vorkommen
- Taggt Metadaten mit gefundenen Keywords
- Nutzen: Vollständiger Export mit zusätzlichen Informationen

## Funktionsweise

1. **Plattform-Erkennung**: Automatische Ermittlung des Chrome-Profil-Pfads
2. **Projekt-Navigation**: Script navigiert zum gewünschten Projekt via URL-Muster
3. **Chat-Filterung**: Unterscheidet normale Chats (`/c/ID`) von Projekt-Chats (`/g/g-p-PROJECT/c/ID`)
4. **URL-basierte Iteration**: Robuste Navigation durch Extraktion aller Chat-URLs vor DOM-Änderungen
5. **Content-Extraktion**: Robuste Selektor-Strategie für verschiedene UI-Versionen
6. **Keyword-Extraktion**: Automatische Erkennung relevanter Begriffe via Häufigkeitsanalyse
7. **Metadaten-Generierung**: SHA256-Hash für Manipulationssicherheit
8. **Keyword-Detection**: Durchsucht Chat-Inhalte, erstellt gezielte Screenshots
9. **Projekt-Ordnerstruktur**: Automatische Organisation in Unterordnern

## Technische Details

- **Browser-Automatisierung**: Playwright mit echtem Chrome-Profil
- **Anti-Bot-Maßnahmen**: WebDriver-Flag wird entfernt
- **Robuste Selektoren**: Mehrere Fallback-Strategien für UI-Änderungen
- **URL-basierte Navigation**: Verhindert DOM-Timeout-Fehler
- **Error-Handling**: Einzelne Fehler brechen Export nicht ab
- **Keyword-Algorithmus**: Häufigkeitsanalyse mit Stopwort-Filterung (DE/EN)
- **Plattform-Unterstützung**: Automatische OS-Erkennung für Chrome-Pfade

## Anwendungsfälle

- **Account-Tracking-Untersuchung**: GDPR-konforme Dokumentation
- **Selektiver Export**: Nur Chats zu bestimmten Projekten/Themen
- **Backup**: Sichere Kopie aller Conversations
- **Recherche**: Keyword-basierte Analyse von Chats
- **Forensik**: Unveränderbare Hashes für Beweissicherung
- **Projekt-Archivierung**: Strukturierte Organisation nach Projekten

## Bekannte Limitierungen

- Benötigt aktive Chrome-Session (kein Headless-Mode für Login)
- Cloudflare-CAPTCHA muss manuell gelöst werden
- UI-Änderungen bei ChatGPT können Selektoren brechen
- Keyword-Extraktion basiert auf Häufigkeit (kein semantisches Verständnis)

## Troubleshooting

### "Keine Chats erkannt"
- Stelle sicher, dass die Sidebar links sichtbar ist
- Warte bis Chats vollständig geladen sind
- Drücke ENTER wenn bereit

### "Projekt nicht gefunden"
- Überprüfe Schreibweise (case-sensitive)
- Stelle sicher, dass Projekt existiert
- Achte auf URL-Änderung in der Console-Ausgabe

### PDF-Generierung schlägt fehl
- Normal bei manchen Chats
- Markdown und HTML werden trotzdem gespeichert

### "TimeoutError" bei Chat-Navigation
- Wurde in v2.1 gefixt durch URL-basierte Navigation
- Bei Problemen: Update auf neueste Version

### Chrome-Profil nicht gefunden
- Überprüfe ob Chrome installiert ist
- Bei nicht-Standard-Profilen: Manuelle Konfiguration nötig (siehe Konfiguration)

## Entwicklung

Entwickelt für Account-Tracking-Untersuchungen zur Dokumentation von Business-Account-Aktivitäten.

### Version History

- **v2.1** (2025-12-13): 
  - Automatische Keyword-Extraktion
  - Filter-Keywords für selektiven Export
  - Plattform-unabhängige Chrome-Profil-Erkennung
  - Projekt-Unterordner
  - URL-basierte Navigation (Fix für Timeout-Fehler)
  - Verbesserte Fehlerbehandlung
  
- **v2.0** (2025-12-13): 
  - Projekt-Support
  - Dynamische Verzeichnisnamen
  - Optionale Keywords
  
- **v1** (2024-11-27): 
  - Basis-Export mit erweiterten Features

## Lizenz

MIT License - siehe LICENSE Datei

## Autor

Andy Post

## Hinweise

- **Wichtig**: Chrome muss komplett geschlossen sein bevor das Script startet
- **GDPR**: Dieses Tool dient der Dokumentation eigener Daten
- **Ethik**: Nur für eigene Accounts verwenden
- **Performance**: Bei großen Exporten (>100 Chats) kann der Export mehrere Minuten dauern

## Support

Bei Problemen bitte GitHub Issues verwenden.

## Roadmap

- [ ] MCP-basierte semantische Keyword-Extraktion (optional)
- [ ] Parallele Chat-Verarbeitung für schnelleren Export
- [ ] Export-Resume bei Unterbrechung
- [ ] Webhook-Benachrichtigung bei Export-Abschluss
