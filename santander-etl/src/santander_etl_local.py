"""
ETL para Santander Dev Week - Versão para API Local
"""
import pandas as pd
import requests
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Adiciona o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

class SantanderETL:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        print(f"🔗 Conectando à API: {api_url}")
        
    def extract_from_csv(self, csv_path):
        """Extrai dados do CSV"""
        print(f"📂 Lendo CSV: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ Arquivo não encontrado: {csv_path}")
            print("📝 Criando CSV de exemplo...")
            self.create_sample_csv(csv_path)
        
        df = pd.read_csv(csv_path)
        print(f"✅ CSV lido: {len(df)} registros")
        return df
    
    def create_sample_csv(self, csv_path):
        """Cria CSV de exemplo se não existir"""
        sample_data = {
            'UserID': [1, 2, 3, 4, 5],
            'name': ['Naruto Uzumaki', 'Hinata Hyuga', 'Sasuke Uchiha', 'Sakura Haruno', 'Kakashi Hatake'],
            'email': ['naruto@konoha.com', 'hinata@konoha.com', 'sasuke@konoha.com', 'sakura@konoha.com', 'kakashi@konoha.com']
        }
        df = pd.DataFrame(sample_data)
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        df.to_csv(csv_path, index=False)
        print(f"✅ CSV de exemplo criado: {csv_path}")
        return df
    
    def check_api_connection(self):
        """Verifica se a API está respondendo"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API está respondendo!")
                return True
        except requests.exceptions.ConnectionError:
            print("❌ API não encontrada. Execute primeiro: uvicorn app.main:app --reload")
            return False
        except Exception as e:
            print(f"⚠️  Erro ao conectar com API: {e}")
            return False
    
    def get_or_create_user(self, user_id, name):
        """Obtém usuário da API ou cria estrutura básica"""
        try:
            # Tenta buscar da API
            response = requests.get(f"{self.api_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Se não conseguir, cria estrutura básica
        return {
            'id': user_id,
            'name': name,
            'account': {
                'id': user_id,
                'number': f'000{user_id}-1',
                'agency': '0001',
                'balance': 1000.0,
                'limit': 5000.0
            },
            'card': {
                'id': user_id,
                'number': f'**** **** **** {user_id:04d}',
                'limit': 10000.0
            },
            'features': [],
            'news': []
        }
    
    def transform(self, users):
        """Transforma dados - gera mensagens personalizadas"""
        print("\n🤖 Gerando mensagens personalizadas...")
        
        # Mensagens de exemplo (substitua por IA se quiser)
        messages = [
            "{name}, invista hoje para garantir seu futuro financeiro!",
            "Olá {name}, seu dinheiro pode trabalhar para você. Comece a investir!",
            "{name}, o Santander tem as melhores opções de investimento para você.",
            "Não deixe seu dinheiro parado, {name}. Invista com sabedoria!",
            "{name}, seu futuro financeiro começa com uma decisão hoje."
        ]
        
        import random
        from datetime import datetime
        
        for user in users:
            # Gera mensagem
            template = random.choice(messages)
            message = template.format(name=user['name'])
            
            # Adiciona à lista de notícias
            new_news = {
                'id': len(user.get('news', [])) + 1,
                'icon': 'https://cdn-icons-png.flaticon.com/512/3135/3135679.png',
                'description': message,
                'date': datetime.now().isoformat()
            }
            
            if 'news' not in user:
                user['news'] = []
            user['news'].append(new_news)
            
            print(f"📝 {user['name']}: {message}")
        
        print("✅ Mensagens geradas!")
        return users
    
    def save_to_json(self, users, output_path):
        """Salva dados em JSON"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos em: {output_path}")
    
    def save_to_csv(self, users, output_path):
        """Salva relatório em CSV"""
        data = []
        for user in users:
            data.append({
                'UserID': user['id'],
                'Nome': user['name'],
                'Conta': user['account']['number'],
                'Saldo': user['account']['balance'],
                'Última_Mensagem': user['news'][-1]['description'] if user['news'] else '',
                'Total_Mensagens': len(user['news'])
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"📊 Relatório CSV: {output_path}")
    
    def run(self):
        """Executa o pipeline ETL completo"""
        print("=" * 80)
        print("🚀 SANTANDER DEV WEEK - ETL PIPELINE")
        print("=" * 80)
        
        # 1. Verifica API
        if not self.check_api_connection():
            print("⚠️  Continuando em modo local...")
        
        # 2. Extrai dados
        csv_path = 'data/SDW2023.csv'
        df = self.extract_from_csv(csv_path)
        
        # 3. Obtém/cria usuários
        users = []
        for _, row in df.iterrows():
            user = self.get_or_create_user(
                user_id=row['UserID'],
                name=row.get('name', f'Cliente {row["UserID"]}')
            )
            users.append(user)
        
        print(f"👥 {len(users)} usuários processados")
        
        # 4. Transforma (gera mensagens)
        users = self.transform(users)
        
        # 5. Salva resultados
        self.save_to_json(users, 'output/users_processed.json')
        self.save_to_csv(users, 'output/users_report.csv')
        
        # 6. Tenta enviar para API (se disponível)
        self.update_api_users(users)
        
        # 7. Relatório final
        self.generate_report(users)
        
        return users
    
    def update_api_users(self, users):
        """Tenta atualizar usuários na API"""
        print("\n🔄 Atualizando API...")
        
        updated = 0
        for user in users[:3]:  # Limita a 3 para teste
            try:
                response = requests.put(
                    f"{self.api_url}/users/{user['id']}",
                    json=user,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print(f"✅ {user['name']} atualizado")
                    updated += 1
                else:
                    print(f"⚠️  {user['name']}: API retornou {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {user['name']}: {e}")
        
        print(f"📊 {updated}/{len(users)} usuários atualizados na API")
    
    def generate_report(self, users):
        """Gera relatório final"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL")
        print("=" * 80)
        
        total_messages = sum(len(user.get('news', [])) for user in users)
        total_balance = sum(user['account']['balance'] for user in users)
        
        print(f"👥 Total de usuários: {len(users)}")
        print(f"📨 Total de mensagens: {total_messages}")
        print(f"💰 Saldo total: R$ {total_balance:,.2f}")
        print(f"📊 Saldo médio: R$ {total_balance/len(users):,.2f}")
        
        print("\n📝 Últimas mensagens geradas:")
        print("-" * 80)
        for user in users[-3:]:
            if user['news']:
                msg = user['news'][-1]['description']
                print(f"{user['name']}: {msg[:70]}...")
        
        print("=" * 80)
        print("✅ Pipeline ETL concluído com sucesso!")
        print("📁 Arquivos gerados:")
        print("   - output/users_processed.json")
        print("   - output/users_report.csv")
        print("=" * 80)

# Execução principal
if __name__ == "__main__":
    # Cria estrutura de diretórios
    os.makedirs('data', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    # Executa ETL
    etl = SantanderETL()
    etl.run()