import csv
import requests

# Configuração do GLPI
GLPI_SERVER = 'https://servicedesk.yhbrasil.com'                        ### - sem barra no final. - Endereço HTTPS/HTTP
APP_TOKEN = 'sAVrq6rM7BF6Vc0c3FTIM2wcBZyqr3pKFnSDsirV'                  ### - API token
USER_TOKEN = 'JXkOa20cLYfMXvHnjh6e3zbgX1K4PM8Yp6UaZFlV'                 ### - Token pessoal

# URL do servidor GLPI
GLPI_URL = f'{GLPI_SERVER}/apirest.php'

# Inicia uma sessão
def init_session():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'user_token {USER_TOKEN}',
        'App-Token': APP_TOKEN
    }

    response = requests.get(f'{GLPI_URL}/initSession', headers=headers)
    if response.status_code == 200:
        return response.json()['session_token']
    else:
        return None

# Encerra uma sessão
def kill_session(session_token):
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': APP_TOKEN
    }

    response = requests.get(f'{GLPI_URL}/killSession', headers=headers)
    return response.status_code == 200

# Cria um chamado
def create_ticket(session_token, ticket_data):
    headers = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': APP_TOKEN
    }

    response = requests.post(f'{GLPI_URL}/Ticket', headers=headers, json=ticket_data)
    return response

# Lê o arquivo CSV e cria os chamados
def read_csv_and_create_tickets(session_token, csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        chamados_criados = []

        for row in reader:
            # Extrai os campos do CSV
            ticket_data = {
                'name': row['Título'],
                'status': row['Status'],
                'impact': row['Impacto'],
                'date': row['Data de abertura'],
                'solvedate': row['Data da solução'],
                'users_id_recipient': row['Requerente - Requerente'],
                #'type': row['Tipo']
                'assigned_technician': row['Atribuído - Técnico'],
                'assigned_group': row['Atribuído - Grupo técnico'],
                'location': row['Localização']
            }

            response = create_ticket(session_token, ticket_data)
            if response.status_code == 201:
                chamado_info = {
                    'id': response.json()['id'],
                    'titulo': ticket_data['name']
                }
                chamados_criados.append(chamado_info)
                print('Chamado criado com sucesso!')
                print('ID do chamado:', chamado_info['id'])
            else:
                print('Erro ao criar chamado:', response.json())

        return chamados_criados

# Executa o script
def main():
    session_token = init_session()
    if session_token is None:
        print('Erro ao iniciar a sessão')
        return

    csv_file_path = 'export.csv'
    chamados_criados = read_csv_and_create_tickets(session_token, csv_file_path)

    print('----- Chamados Criados -----')
    for chamado in chamados_criados:
        print(f'ID: {chamado["id"]} | Título: {chamado["titulo"]}')

    with open('chamados_criados.txt', 'w') as output_file:
        output_file.write('----- Chamados Criados -----\n')
        for chamado in chamados_criados:
            output_file.write(f'ID: {chamado["id"]} | Título: {chamado["titulo"]}\n')

    if not kill_session(session_token):
        print('Erro ao encerrar a sessão')

if __name__ == '__main__':
    main()
