import streamlit as st
import subprocess
import pandas as pd
import time
import os

# Passwort aus Umgebungsvariable holen oder Standardpasswort verwenden
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "standardpasswort123")

# Passwortschutz
def check_password():
    """Einfache Passwortüberprüfung mit Umgebungsvariable"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
        
    if st.session_state.password_correct:
        return True
        
    password = st.text_input("Bitte gib das Passwort ein:", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.password_correct = True
        st.rerun()
        return True
    elif password:
        st.error("Das eingegebene Passwort ist falsch.")
    return False

# Hauptfunktion für die Prozessüberwachung
def main():
    st.title('Live Überwachung der Python-Prozesse im work-Verzeichnis')
    
    # Platzhalter für die Tabelle
    placeholder = st.empty()
    
    # Endlosschleife für automatische Updates
    while True:
        command = "ps aux | grep '[p]ython' | awk '$11 ~ /work\\// {print $2 \";\" $6/1024 \";\" $11 \" \" $12 \" \" $13 \" \" $14}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout.strip().split('\n')
        
        processes = []
        for line in output:
            if line:
                parts = line.split(';', 2)
                if len(parts) == 3:
                    pid = parts[0].strip()
                    try:
                        mem_mb = float(parts[1].strip())
                    except ValueError:
                        mem_mb = 0.0
                    cmd = parts[2].strip()
                    processes.append({'PID': pid, 'Memory (MB)': round(mem_mb, 2), 'Command': cmd})
        
        df = pd.DataFrame(processes)
        
        with placeholder.container():
            if not df.empty:
                st.write("Aktuelle Python-Prozesse im work-Verzeichnis:")
                st.dataframe(df, use_container_width=True)
                total_memory = df['Memory (MB)'].sum()
                st.write(f"**Gesamtspeicherverbrauch:** {total_memory:.2f} MB")
            else:
                st.write("Keine Python-Prozesse im work-Verzeichnis gefunden.")
        time.sleep(3)  # Aktualisierung alle 3 Sekunden

# App starten mit Passwortschutz
if check_password():
    main()

