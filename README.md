# ChatGPT Business Export Tool

Python-Script zum automatisierten Export von ChatGPT Business Account Conversations mit Unterstützung für Projekte, Metadaten und Keyword-Suche.

## Features

- **Projekt-Support**: Exportiere Chats aus spezifischen Projekten oder alle Chats
- **Vollständige Metadaten**: SHA256-Hash, Timestamps, URLs für jeden Chat
- **Multiple Formate**: Markdown, PDF, HTML-Rohdaten
- **Screenshots**: Vollbild-Screenshots und gezielte Keyword-Screenshots
- **Keyword-Suche**: Durchsuche Chats nach spezifischen Begriffen
- **Backup-Unterstützung**: Automatisches Kopieren zu konfigurierten Backup-Orten
- **Account-Tracking**: Dokumentation für GDPR-Untersuchungen

## Voraussetzungen

- Python 3.8+
- Google Chrome
- Playwright für Python

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

3. Chrome-Profil-Pfad anpassen:
Öffne `export_enhanced_v2.py` und passe `USER_DATA_DIR` an (Zeile 10):
```python
USER_DATA_DIR = r"C:\Users\DEIN-USER\AppData\Local\Google\Chrome\User Data\Profile 1"
```

## Verwendung

### Basis-Export (nur Chats außerhalb von Projekten)
```bash
python export_enhanced_v2.py
```

### Export aus einem spezifischen Projekt
```bash
python export_enhanced_v2.py --project "Projektname"
```

### Export aller Chats (inkl. Projekte)
```bash
python export_enhanced_v2.py --all
```

### Mit Keyword-Suche
```bash
python export_enhanced_v2.py --keywords NRW "Bad Sassendorf" OWL
```

### Kombiniert
```bash
python export_enhanced_v2.py --project "MCP" --keywords NRW OWL
```

## Ausgabestruktur

Das Script erstellt folgende Ordnerstruktur:

```
chatgpt_business_export_project_mcp_20251213_155623/
├── markdown/           # Chat-Inhalte als Markdown
├── pdf/               # PDFs der Chats
├── metadata/          # JSON mit Hash, URL, Keywords
├── screenshots/       # Vollbild + Keyword-Screenshots
├── raw_html/          # HTML-Quelldaten
└── export_info.json   # System-Informationen
```

### Verzeichnisname

Der Exportordner wird automatisch benannt:
- Basis: `chatgpt_business_export_YYYYMMDD_HHMMSS`
- Mit Projekt: `chatgpt_business_export_project_NAME_YYYYMMDD_HHMMSS`
- Mit Keywords: `chatgpt_business_export_kw_KEYWORD1_KEYWORD2_YYYYMMDD_HHMMSS`

## Metadaten-Format

Jeder Chat erhält eine JSON-Metadatendatei:

```json
{
  "export_timestamp": "2025-12-13T15:56:23",
  "chat_timestamp": "2025-12-13T15-56-23",
  "chat_url": "https://chatgpt.com/c/abc123",
  "chat_title": "beispiel-chat",
  "project": "MCP",
  "user_agent": "Mozilla/5.0...",
  "account_info": "ChatGPT Business Account",
  "sha256_markdown": "a1b2c3...",
  "browser": "Chrome",
  "keywords_found": ["NRW", "OWL"]
}
```

## Konfiguration

### Chrome-Profil
```python
USER_DATA_DIR = r"C:\Users\DEIN-USERNAME\AppData\Local\Google\Chrome\User Data\Profile 1"
```

### Backup-Orte (optional)
```python
BACKUP_LOCATIONS = [
    r"D:\Backups\ChatGPT",
    r"E:\USB_Stick\ChatGPT",
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
| `--keywords WORD1 WORD2` | Suche nach Keywords, erstelle Keyword-Screenshots |

## Funktionsweise

1. **Projekt-Navigation**: Script navigiert zum gewünschten Projekt via URL-Muster
2. **Chat-Filterung**: Unterscheidet normale Chats (`/c/ID`) von Projekt-Chats (`/g/g-p-PROJECT/c/ID`)
3. **Content-Extraktion**: Robuste Selektor-Strategie für verschiedene UI-Versionen
4. **Metadaten-Generierung**: SHA256-Hash für Manipulationssicherheit
5. **Keyword-Detection**: Durchsucht Chat-Inhalte, erstellt gezielte Screenshots

## Technische Details

- **Browser-Automatisierung**: Playwright mit echtem Chrome-Profil
- **Anti-Bot-Maßnahmen**: WebDriver-Flag wird entfernt
- **Robuste Selektoren**: Mehrere Fallback-Strategien für UI-Änderungen
- **Error-Handling**: Einzelne Fehler brechen Export nicht ab

## Anwendungsfälle

- **Account-Tracking-Untersuchung**: GDPR-konforme Dokumentation
- **Backup**: Sichere Kopie aller Conversations
- **Recherche**: Keyword-basierte Analyse von Chats
- **Forensik**: Unveränderbare Hashes für Beweissicherung

## Bekannte Limitierungen

- Benötigt aktive Chrome-Session (kein Headless-Mode für Login)
- Cloudflare-CAPTCHA muss manuell gelöst werden
- UI-Änderungen bei ChatGPT können Selektoren brechen

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

## Entwicklung

Entwickelt für Account-Tracking-Untersuchungen zur Dokumentation von Business-Account-Aktivitäten.

### Version History
- **v2** (2025-12-13): Projekt-Support, dynamische Verzeichnisnamen, optionale Keywords
- **v1** (2024-11-27): Basis-Export mit erweiterten Features

## Lizenz

MIT License - siehe LICENSE Datei

## Autor

Andy Post

## Hinweise

- **Wichtig**: Chrome muss komplett geschlossen sein bevor das Script startet
- **GDPR**: Dieses Tool dient der Dokumentation eigener Daten
- **Ethik**: Nur für eigene Accounts verwenden

## Support

Bei Problemen bitte GitHub Issues verwenden.
