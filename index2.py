import sqlite3
import os
from datetime import datetime


# Função para converter imagem para bytes (sem PIL)
def imagem_para_bytes(caminho_imagem):
    """Converte uma imagem para bytes para armazenar no banco"""
    try:
        if os.path.exists(caminho_imagem):
            with open(caminho_imagem, 'rb') as f:
                return f.read()
        else:
            print(f"⚠️  Imagem não encontrada: {caminho_imagem}")
            return None
    except Exception as e:
        print(f"❌ Erro ao ler imagem: {e}")
        return None

# Função para criar o banco de dados e tabela
def criar_banco():
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plantas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nome_cientifico TEXT NOT NULL,
            descricao TEXT NOT NULL,
            caminho_imagem TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados 'plantas.db' criado com sucesso!")

# Função para inserir planta
def inserir_planta(nome, nome_cientifico, descricao, caminho_imagem=None):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO plantas (nome, nome_cientifico, descricao, caminho_imagem)
        VALUES (?, ?, ?, ?)
    ''', (nome, nome_cientifico, descricao, caminho_imagem))
    
    conn.commit()
    conn.close()
    print(f"✅ Planta '{nome}' inserida com sucesso!")

# Função para listar todas as plantas
def listar_plantas():
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM plantas ORDER BY nome')
    plantas = cursor.fetchall()
    
    if not plantas:
        print("❌ Nenhuma planta cadastrada!")
        conn.close()
        return
    
    print("\n🌿" + "="*70)
    print("📋 LISTA DE PLANTAS")
    print("="*70)
    
    for planta in plantas:
        print(f"\n🆔 ID: {planta[0]}")
        print(f"🌱 Nome: {planta[1]}")
        print(f"🔬 Nome Científico: {planta[2]}")
        print(f"📝 Descrição: {planta[3][:80]}...")
        print(f"🖼️  Imagem: {'✅ Sim' if planta[4] else '❌ Não'}")
        print(f"📅 Cadastrada: {planta[5][:10]}")
        print("-" * 70)
    
    conn.close()

# Função para buscar planta por nome
def buscar_planta(nome):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM plantas WHERE nome LIKE ? OR nome_cientifico LIKE ?', 
                   (f'%{nome}%', f'%{nome}%'))
    planta = cursor.fetchone()
    
    if planta:
        print(f"\n🌿" + "="*50)
        print(f"PLANTA ENCONTRADA")
        print("="*50)
        print(f"🆔 ID: {planta[0]}")
        print(f"🌱 Nome: {planta[1]}")
        print(f"🔬 Nome Científico: {planta[2]}")
        print(f"📝 Descrição:\n{planta[3]}")
        print(f"🖼️  Imagem: {planta[4] or 'Nenhuma'}")
        print("="*50)
        conn.close()
        return planta
    else:
        print(f"❌ Planta '{nome}' não encontrada!")
        conn.close()
        return None

# Função para copiar imagem para pasta do projeto
def copiar_imagem_planta(id_planta):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT caminho_imagem FROM plantas WHERE id = ?', (id_planta,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] and os.path.exists(resultado[0]):
        nome_arquivo = f"planta_{id_planta}.jpg"
        try:
            with open(resultado[0], 'rb') as origem:
                with open(nome_arquivo, 'wb') as destino:
                    destino.write(origem.read())
            print(f"✅ Imagem copiada para '{nome_arquivo}'")
        except Exception as e:
            print(f"❌ Erro ao copiar imagem: {e}")
    else:
        print("❌ Imagem não encontrada!")
    
    conn.close()

# Popular com exemplos
def popular_banco_exemplo():
    plantas_exemplo = [
        ("Samambaia", "Nephrolepis exaltata", 
         "Planta ornamental de folhagem verde brilhante. Prefere sombra parcial e solo úmido. "
         "Ideal para ambientes internos. Fácil de cuidar e purifica o ar."),
        
        ("Espada de São Jorge", "Sansevieria trifasciata", 
         "Planta muito resistente. Tolera pouca luz e regas esparsas. "
         "Suas folhas longas são decorativas. Ótima para iniciantes."),
        
        ("Jiboia", "Epipremnum aureum", 
         "Trepadeira popular para pendurar. Cresce rapidamente em meia-sombra. "
         "Folhas variegadas muito bonitas. Cuidado com pets (tóxica)."),
        
        ("Lírio da Paz", "Spathiphyllum wallisii", 
         "Folhagem verde escura com flores brancas elegantes. Adora sombra e umidade. "
         "Excelente purificadora de ar. Floresce várias vezes."),
        
        ("Bromélia", "Guzmania spp.", 
         "Planta exótica com inflorescência colorida. Prefere luz indireta e umidade alta. "
         "Cada planta floresce uma vez, mas produz filhotes.")
    ]
    
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    for nome, nome_cient, desc in plantas_exemplo:
        cursor.execute('INSERT OR IGNORE INTO plantas (nome, nome_cientifico, descricao) VALUES (?, ?, ?)',
                      (nome, nome_cient, desc))
    
    conn.commit()
    conn.close()
    print("✅ 5 plantas de exemplo adicionadas!")

# MENU PRINCIPAL
def menu():
    criar_banco()  # Cria o banco automaticamente
    
    while True:
        print("\n" + "🌿"*20)
        print("    BANCO DE PLANTAS")
        print("🌿"*20)
        print("1. 📋 Listar todas")
        print("2. 🔍 Buscar planta")
        print("3. ➕ Nova planta")
        print("4. 🌱 Exemplos")
        print("5. 🖼️  Copiar imagem")
        print("6. 🗑️  Deletar planta")
        print("0. 🚪 Sair")
        
        opcao = input("\n👉 Escolha: ").strip()
        
        if opcao == "1":
            listar_plantas()
        elif opcao == "2":
            nome = input("Nome da planta: ")
            buscar_planta(nome)
        elif opcao == "3":
            nome = input("🌱 Nome: ")
            nome_cient = input("🔬 Nome científico: ")
            descricao = input("📝 Descrição: ")
            caminho = input("🖼️  Caminho da imagem (opcional): ") or None
            inserir_planta(nome, nome_cient, descricao, caminho)
        elif opcao == "4":
            popular_banco_exemplo()
        elif opcao == "5":
            try:
                id_planta = int(input("🆔 ID da planta: "))
                copiar_imagem_planta(id_planta)
            except:
                print("❌ ID inválido!")
        elif opcao == "6":
            try:
                id_planta = int(input("🆔 ID para deletar: "))
                conn = sqlite3.connect('plantas.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM plantas WHERE id = ?', (id_planta,))
                conn.commit()
                conn.close()
                print("✅ Planta deletada!")
            except:
                print("❌ Erro ao deletar!")
        elif opcao == "0":
            print("👋 Até logo! 🌿")
            break
        else:
            print("❌ Opção inválida!")

# Executar
if __name__ == "__main__":
    print("🌿 Iniciando Banco de Plantas...")
    menu()