import sqlite3
import os
from PIL import Image
import io
import base64
from datetime import datetime

# Função para converter imagem para bytes
def imagem_para_bytes(caminho_imagem):
    """Converte uma imagem para bytes para armazenar no banco"""
    try:
        with open(caminho_imagem, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Imagem não encontrada: {caminho_imagem}")
        return None

# Função para criar o banco de dados e tabela
def criar_banco():
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    # Criar tabela plantas
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
    print("✅ Banco de dados 'plantas.db' criado com sucesso!")

# Função para inserir planta
def inserir_planta(nome, nome_cientifico, descricao, caminho_imagem=None):
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

# Função para listar todas as plantas
def listar_plantas():
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM plantas')
    plantas = cursor.fetchall()
    
    print("\n🌿 LISTA DE PLANTAS:")
    print("-" * 80)
    for planta in plantas:
        print(f"ID: {planta[0]}")
        print(f"Nome: {planta[1]}")
        print(f"Nome Científico: {planta[2]}")
        print(f"Descrição: {planta[3][:100]}...")
        print(f"Data: {planta[5]}")
        print("-" * 80)
    
    conn.close()

# Função para buscar planta por nome
def buscar_planta(nome):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM plantas WHERE nome LIKE ?', (f'%{nome}%',))
    planta = cursor.fetchone()
    
    if planta:
        print(f"\n🌿 PLANTA ENCONTRADA:")
        print(f"Nome: {planta[1]}")
        print(f"Nome Científico: {planta[2]}")
        print(f"Descrição: {planta[3]}")
        return planta
    else:
        print(f"❌ Planta '{nome}' não encontrada!")
        return None
    
    conn.close()

# Função para visualizar imagem da planta (salva em arquivo)
def salvar_imagem_planta(id_planta, nome_arquivo="imagem_planta.jpg"):
    conn = sqlite3.connect('plantas.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT imagem FROM plantas WHERE id = ?', (id_planta,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0]:
        with open(nome_arquivo, 'wb') as f:
            f.write(resultado[0])
        print(f"✅ Imagem salva como '{nome_arquivo}'")
    else:
        print("❌ Nenhuma imagem encontrada para esta planta!")
    
    conn.close()

# Exemplo de uso com plantas reais
def popular_banco_exemplo():
    plantas_exemplo = [
        {
            "nome": "Samambaia",
            "nome_cientifico": "Nephrolepis exaltata",
            "descricao": "Planta ornamental de folhagem verde brilhante. Prefere sombra parcial e solo úmido. Ideal para ambientes internos com boa luminosidade indireta. Fácil de cuidar e purifica o ar."
        },
        {
            "nome": "Espada de São Jorge",
            "nome_cientifico": "Sansevieria trifasciata",
            "descricao": "Planta resistente e purificadora de ar. Tolera pouca luz e regas esparsas. Suas folhas longas e verticais são muito decorativas. Ótima para iniciantes."
        },
        {
            "nome": "Jiboia",
            "nome_cientifico": "Epipremnum aureum",
            "descricao": "Trepadeira popular para pendurar. Cresce rapidamente em meia-sombra. Suas folhas variegadas são muito bonitas. Cuidado com pets, é tóxica se ingerida."
        },
        {
            "nome": "Lírio da Paz",
            "nome_cientifico": "Spathiphyllum wallisii",
            "descricao": "Planta de folhagem verde escura com flores brancas elegantes. Adora sombra e umidade. Excelente purificadora de ar. Floresce várias vezes ao ano."
        },
        {
            "nome": "Bromélia",
            "nome_cientifico": "Guzmania spp.",
            "descricao": "Planta exótica com inflorescência colorida. Prefere luz indireta e umidade alta. Cada planta floresce uma vez na vida, mas produz filhotes. Muito decorativa."
        }
    ]
    
    print("🌱 Populando banco com plantas de exemplo...")
    for planta in plantas_exemplo:
        inserir_planta(planta["nome"], planta["nome_cientifico"], planta["descricao"])
    print("✅ Banco populado com sucesso!")

# MENU PRINCIPAL
def menu():
    while True:
        print("\n🌿 BANCO DE DADOS DE PLANTAS")
        print("1. Criar banco de dados")
        print("2. Popular com exemplos")
        print("3. Listar todas as plantas")
        print("4. Buscar planta")
        print("5. Inserir nova planta")
        print("6. Salvar imagem de planta")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            criar_banco()
        elif opcao == "2":
            popular_banco_exemplo()
        elif opcao == "3":
            listar_plantas()
        elif opcao == "4":
            nome = input("Digite o nome da planta: ")
            buscar_planta(nome)
        elif opcao == "5":
            nome = input("Nome da planta: ")
            nome_cient = input("Nome científico: ")
            descricao = input("Descrição: ")
            caminho_img = input("Caminho da imagem (opcional): ")
            inserir_planta(nome, nome_cient, descricao, caminho_img if caminho_img else None)
        elif opcao == "6":
            id_planta = int(input("ID da planta: "))
            salvar_imagem_planta(id_planta)
        elif opcao == "0":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

# Executar o programa
if __name__ == "__main__":
    menu()