"""
Serveur web interactif pour Kidney Exchange
Lance avec: python server.py
Puis ouvre: http://localhost:5000
"""
from flask import Flask, render_template_string, request, jsonify
import sys
import os
import traceback

# Importer le module principal en lisant le fichier
script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(script_dir, 'etape 2')

# Charger le code du script principal
with open(script_path, 'r', encoding='utf-8') as f:
    script_code = f.read()

# Exécuter tout sauf le if __name__ == "__main__"
# On va seulement prendre les imports et les classes
lines = script_code.split('\n')
code_to_exec = []
skip_main = False
for line in lines:
    if 'if __name__ == "__main__"' in line:
        skip_main = True
    if not skip_main:
        code_to_exec.append(line)

exec('\n'.join(code_to_exec), globals())

app = Flask(__name__)

# Cache pour éviter de régénérer trop souvent
cache = {'n_patients': 20, 'html': None}

def generate_data(n_patients):
    """Génère les données et retourne le HTML"""
    try:
        eng = MedicalEngine(n_patients=n_patients)
        success = eng.load_and_merge()
        if success:
            eng.run_ai_scoring()
            eng.run_game_theory()
            data = eng.export()
            renderer = WebRenderer(*data)
            return renderer.build_html()
    except Exception as e:
        return f"<h1>Erreur: {e}</h1><pre>{traceback.format_exc()}</pre>"

@app.route('/')
def index():
    """Page principale"""
    n_patients = int(request.args.get('n', cache['n_patients']))
    
    # Régénérer si nombre différent
    if n_patients != cache['n_patients'] or cache['html'] is None:
        print(f"🔄 Génération pour {n_patients} patients...")
        cache['n_patients'] = n_patients
        cache['html'] = generate_data(n_patients)
    
    return cache['html']

@app.route('/regenerate', methods=['POST'])
def regenerate():
    """API pour régénérer avec AJAX"""
    n_patients = int(request.json.get('n', 20))
    print(f"🔄 Régénération AJAX pour {n_patients} patients...")
    cache['n_patients'] = n_patients
    cache['html'] = generate_data(n_patients)
    return jsonify({'success': True, 'n': n_patients})

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 KIDNEY EXCHANGE - Serveur Interactif")
    print("=" * 60)
    print("\n📡 Serveur démarré sur: http://localhost:5000")
    print("🎛️  Change le nombre de patients directement dans le site !")
    print("\n⏹️  Pour arrêter: Ctrl+C\n")
    
    # Génération initiale
    cache['html'] = generate_data(20)
    
    app.run(debug=True, port=5000, use_reloader=False)
