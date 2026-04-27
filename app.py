from flask import Flask, render_template, request, jsonify, send_file, Response
import sqlite3
import os
import base64
from io import BytesIO
from PIL import Image
import io

app = Flask(__name__)

# ========================================
# FUNÇÕES DO BANCO
# ========================================

def imagem_para_bytes(caminho_imagem):
    """Converte uma imagem para bytes para armazenar no banco"""
    try:
        with open(caminho_imagem, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Imagem não encontrada: {caminho_imagem}")
        return None

def criar_banco():
    """Cria o banco de dados e tabela"""
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plantas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nome_cientifico TEXT NOT NULL,
            descricao TEXT NOT NULL,
            imagem BLOB,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados 'plantas.db' criado/atualizado!")

def inserir_planta(nome, nome_cientifico, descricao, caminho_imagem=None):
    """Insere uma nova planta no banco"""
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    imagem_blob = imagem_para_bytes(caminho_imagem) if caminho_imagem else None
    
    cursor.execute('''
        INSERT INTO plantas (nome, nome_cientifico, descricao, imagem)
        VALUES (?, ?, ?, ?)
    ''', (nome, nome_cientifico, descricao, imagem_blob))
    
    conn.commit()
    conn.close()
    print(f"✅ Planta '{nome}' inserida com sucesso!")

def listar_plantas_json():
    """Lista todas as plantas em formato JSON para a interface web"""
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plantas ORDER BY nome')
    plantas = cursor.fetchall()
    conn.close()
    
    resultado = []
    for planta in plantas:
        imagem_b64 = None
        if planta[4]:
            try:
                imagem_b64 = base64.b64encode(planta[4]).decode('utf-8')
            except:
                imagem_b64 = None
        
        resultado.append({
            'id': planta[0],
            'nome': planta[1],
            'nome_cientifico': planta[2],
            'descricao': planta[3],
            'imagem_b64': imagem_b64,
            'data_cadastro': str(planta[5])
        })
    return resultado

# ========================================
# ROTAS FLASK
# ========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listar')
def listar():
    plantas = listar_plantas_json()
    return render_template('listar.html', plantas=plantas)

@app.route('/buscar', methods=['GET'])
def buscar():
    nome = request.args.get('nome', '')
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plantas WHERE nome LIKE ?', (f'%{nome}%',))
    planta = cursor.fetchone()
    conn.close()
    
    if planta:
        imagem_b64 = None
        if planta[4]:
            try:
                imagem_b64 = base64.b64encode(planta[4]).decode('utf-8')
            except:
                pass
        
        return jsonify({
            'encontrada': True,
            'planta': {
                'id': planta[0],
                'nome': planta[1],
                'nome_cientifico': planta[2],
                'descricao': planta[3],
                'imagem_b64': imagem_b64
            }
        })
    return jsonify({'encontrada': False, 'mensagem': 'Planta não encontrada'})

@app.route('/adicionar', methods=['POST'])
def adicionar():
    try:
        nome = request.form['nome']
        nome_cient = request.form['nome_cientifico']
        descricao = request.form['descricao']
        
        inserir_planta(nome, nome_cient, descricao)
        return jsonify({'sucesso': True, 'mensagem': f'Planta "{nome}" adicionada!'})
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/imagem/<int:id_planta>')
def imagem(id_planta):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT imagem, nome FROM plantas WHERE id = ?', (id_planta,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado and resultado[0]:
        return send_file(
            BytesIO(resultado[0]),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'{resultado[1].replace(" ", "_")}.jpg'
        )
    return "Imagem não encontrada", 404

@app.route('/popular_exemplo')
def popular_exemplo():
    """🔥 ROTA MANUAL - Só funciona quando clicar no botão"""
    plantas_exemplo = [
        {"nome": "Samambaia", "nome_cientifico": "Nephrolepis exaltata", 
         "descricao": "Planta ornamental de folhagem verde brilhante. Prefere sombra parcial."},
        {"nome": "Espada de São Jorge", "nome_cientifico": "Sansevieria trifasciata", 
         "descricao": "Planta resistente e purificadora de ar. Tolera pouca luz."},
        {"nome": "Jiboia", "nome_cientifico": "Epipremnum aureum", 
         "descricao": "Trepadeira popular para pendurar. Cresce rapidamente."}
    ]
    
    for planta in plantas_exemplo:
        inserir_planta(planta["nome"], planta["nome_cientifico"], planta["descricao"])
    
    return jsonify({'sucesso': True, 'mensagem': '✅ 3 plantas de exemplo adicionadas!'})

@app.route('/api/plantas')
def api_plantas():
    """API JSON completa das plantas"""
    return jsonify(listar_plantas_json())

# ========================================
# INICIALIZAÇÃO (SEM POP-UP AUTOMÁTICO)
# ========================================

if __name__ == '__main__':
    # ✅ APENAS cria o banco, NÃO popula automaticamente
    criar_banco()
    print("🌿 Servidor Flask iniciado!")
    print("📱 http://localhost:5000")
    print("🔥 Para exemplos: http://localhost:5000/popular_exemplo")
    print("📋 Ver todas: http://localhost:5000/listar")
    app.run(debug=True, port=5000, host='0.0.0.0')