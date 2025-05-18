from flask import Flask, render_template_string, request, redirect, url_for, session
import subprocess
import time
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Für die Session-Verwaltung

# Passwort aus Umgebungsvariable holen oder Standardpasswort verwenden
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "standardpasswort123")

# HTML-Template als String
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PStop - Python Process Monitor</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .total {
            margin-top: 20px;
            font-weight: bold;
            font-size: 18px;
        }
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            margin-top: 10px;
        }
        .logout {
            float: right;
        }
    </style>
</head>
<body>
    {% if logged_in %}
        <div class="container">
            <h1>PStop - Python Process Monitor</h1>
            <a href="/logout" class="logout"><button>Logout</button></a>
            <div id="process-table">
                <!-- Hier werden die Prozessdaten eingefügt -->
            </div>
            <script>
                function updateProcesses() {
                    fetch('/api/processes')
                        .then(response => response.json())
                        .then(data => {
                            let tableHtml = '';
                            if (data.processes.length > 0) {
                                tableHtml = `
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>PID</th>
                                                <th>Memory (MB)</th>
                                                <th>Command</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                `;
                                
                                data.processes.forEach(process => {
                                    tableHtml += `
                                        <tr>
                                            <td>${process.PID}</td>
                                            <td>${process.Memory}</td>
                                            <td>${process.Command}</td>
                                        </tr>
                                    `;
                                });
                                
                                tableHtml += `
                                        </tbody>
                                    </table>
                                    <div class="total">Gesamtspeicherverbrauch: ${data.total_memory} MB</div>
                                `;
                            } else {
                                tableHtml = '<p>Keine Python-Prozesse im work-Verzeichnis gefunden.</p>';
                            }
                            
                            document.getElementById('process-table').innerHTML = tableHtml;
                        })
                        .catch(error => console.error('Error fetching process data:', error));
                }
                
                // Initial update
                updateProcesses();
                
                // Update every 3 seconds
                setInterval(updateProcesses, 3000);
            </script>
        </div>
    {% else %}
        <div class="login-container">
            <h1>Login</h1>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <form method="post" action="/login">
                <div class="form-group">
                    <label for="password">Passwort:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
    {% endif %}
</body>
</html>
"""

# Login-Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Funktion zum Abrufen der Prozessinformationen
def get_python_work_processes():
    command = "ps aux | grep '[p]ython' | awk '$11 ~ /work\\// {print $2 \";\" $6/1024 \";\" $11 \" \" $12 \" \" $13 \" \" $14}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout.strip().split('\n')
    
    processes = []
    total_memory = 0
    
    for line in output:
        if line:
            parts = line.split(';', 2)
            if len(parts) == 3:
                pid = parts[0].strip()
                try:
                    mem_mb = float(parts[1].strip())
                    total_memory += mem_mb
                except ValueError:
                    mem_mb = 0.0
                cmd = parts[2].strip()
                processes.append({'PID': pid, 'Memory': round(mem_mb, 2), 'Command': cmd})
    
    return processes, round(total_memory, 2)

# Routen
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, logged_in=session.get('logged_in', False), error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Falsches Passwort'
    return render_template_string(HTML_TEMPLATE, logged_in=session.get('logged_in', False), error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/processes')
@login_required
def api_processes():
    processes, total_memory = get_python_work_processes()
    return json.dumps({'processes': processes, 'total_memory': total_memory})

if __name__ == '__main__':
    # Standardmäßig läuft Flask nur auf localhost. Für Netzwerkzugriff:
    # app.run(host='0.0.0.0', port=8060, debug=False)
    app.run(debug=True)

