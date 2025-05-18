# PStop - Python Process Monitor

PStop ist ein einfaches, aber leistungsfähiges Tool zur Überwachung von Python-Prozessen in Echtzeit. Es wurde speziell entwickelt, um Python-Prozesse in einem bestimmten Arbeitsverzeichnis zu überwachen und deren Speicherverbrauch anzuzeigen.

## Funktionen

- Echtzeit-Überwachung von Python-Prozessen im `work/`-Verzeichnis
- Anzeige von PID, Speicherverbrauch und vollständigem Befehl
- Berechnung des Gesamtspeicherverbrauchs aller überwachten Prozesse
- Automatische Aktualisierung alle 3 Sekunden
- Passwortschutz über Umgebungsvariable

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- pip (Python-Paketmanager)

### Abhängigkeiten installieren

```bash
pip install streamlit pandas
```

### Konfiguration

1. Klone oder lade das Repository herunter:
```bash
git clone https://github.com/yourusername/pstop.git
cd pstop
```

2. Setze das Admin-Passwort als Umgebungsvariable:
```bash
export ADMIN_PASSWORD="dein_sicheres_passwort"
```

## Verwendung

### Lokale Ausführung

Starte die App mit:

```bash
streamlit run process_monitor.py
```

### Netzwerkzugriff ermöglichen

Um die App über das Netzwerk zugänglich zu machen:

```bash
streamlit run process_monitor.py --server.port 8060 --server.address 0.0.0.0
```

### Hinter einem Reverse Proxy (Nginx)

Wenn du die App hinter einem Nginx-Reverse-Proxy betreiben möchtest, verwende folgende Konfiguration:

```nginx
server {
    listen 80;
    server_name deine-subdomain.dein-domain-name.de;

    location / {
        proxy_pass http://127.0.0.1:8060/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_redirect off;
    }
}
```

## Anpassung

### Filter für andere Verzeichnisse

Standardmäßig überwacht PStop Python-Prozesse im `work/`-Verzeichnis. Um ein anderes Verzeichnis zu überwachen, ändere den `awk`-Filter in der `command`-Variable:

```python
command = "ps aux | grep '[p]ython' | awk '$11 ~ /dein_verzeichnis\\// {print $2 \";\" $6/1024 \";\" $11 \" \" $12 \" \" $13 \" \" $14}'"
```

### Aktualisierungsintervall ändern

Um das Aktualisierungsintervall zu ändern, passe den Wert in der `time.sleep()`-Funktion an:

```python
time.sleep(5)  # Aktualisierung alle 5 Sekunden
```

## Sicherheit

- Das Passwort wird über die Umgebungsvariable `ADMIN_PASSWORD` gesetzt
- Falls die Variable nicht gesetzt ist, wird ein Standardpasswort verwendet
- Für erhöhte Sicherheit solltest du die App hinter einem HTTPS-Proxy betreiben

## Fehlerbehebung

### Keine Prozesse werden angezeigt

Überprüfe, ob Python-Prozesse im `work/`-Verzeichnis laufen:

```bash
ps aux | grep '[p]ython' | grep work/
```

### Probleme mit WebSockets

Bei Problemen mit WebSockets hinter einem Proxy, stelle sicher, dass die Proxy-Konfiguration die WebSocket-Header korrekt weiterleitet.

## Lizenz

MIT

## Autor

Erstellt mit Unterstützung von KI-Tools.
