import psutil
import time
import platform
import datetime
from mysql.connector import connect
import requests
import json
import pymssql

# Função para obter a conexão com o banco de dados
def mysql_connection(host, user, passwd, database=None):
    connection = connect(
        host=host,
        user=user,
        passwd=passwd,
        database=database
    )
    return connection
# Conectar ao banco de dados
connection = mysql_connection('localhost', 'root', 'urubu100', 'HealthTouch')

sql_server_connection = pymssql.connect(server='54.145.218.19', database='HealthTouch', user='sa', password='urubu100')

def insert_data(connection, query, values):
    cursor = sql_server_connection.cursor()
    cursor.execute(query, values)
    connection.commit()


print("Bem Vindo à Aplicação Health Touch")
email = input("Digite seu e-mail:")
senha = input("Digite sua senha:")
cursor = connection.cursor()


# puxando todos os dados do colaborador
query = "SELECT * FROM Colaborador WHERE email = %s AND senha = %s"
#cursor.execute(query, (email, senha))
cursor.execute(query, (email, senha))
resultado = cursor.fetchone()

# puxando somente o nome do colaborador
query = "SELECT nome FROM Colaborador WHERE email = %s AND senha = %s"
#cursor.execute(query, (email, senha))
cursor.execute(query, (email, senha))
nome = cursor.fetchone()
# puxando a fkEmpresa
query = "SELECT fkEmpresa FROM Colaborador WHERE email = %s AND senha = %s"
#cursor.execute(query, (email, senha))
cursor.execute(query, (email, senha))
fkEmpresa = cursor.fetchone()

# puxando o cargo
query = "SELECT fkNivelAcesso FROM Colaborador WHERE email = %s AND senha = %s"
#cursor.execute(query, (email, senha))
cursor.execute(query, (email, senha))
fkNivelAcesso = cursor.fetchone()


# completando o nome dos cargos
if fkNivelAcesso:
    fkNivelAcesso = fkNivelAcesso[0]

    if fkNivelAcesso == 1:
        cargo = "Representante Legal"
    elif fkNivelAcesso == 2:
        cargo = "Gerente de TI"
    elif fkNivelAcesso == 3:
        cargo = "Equipe de TI"

# validando login
if resultado:
    print('\r\n')
    print(f"Login bem-sucedido. Logado como {nome[0]} - {cargo}")

    # conectando com o workbench para fazer os inserts
    def mysql_connection(host, user, passwd, database=None):
        connection = connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database
        )
  return connection

    # aqui colocar suas credencias do banco
    #connection = mysql_connection('localhost', 'root', 'Biel0501', 'HealthTouch')
    #connectionSql = pymssql.connect(server='54.145.218.19', database='HealthTouch', user='sa', password='urubu100')

    # puxando todas as máquinas cadastradas
    query = "select idMaquina, SO, IP, sala, andar, nome from Maquina JOIN LocalSala on fkLocal = idLocalSala join setor on fkSetor = idSetor;"
    cursor.execute(query)
    maquinas = cursor.fetchall()

    # printando as máquinas disponíveis
    print('\r\n')
    print('Lista de máquinas disponíveis para monitoramento:\r\n')
    for maquina in maquinas:
        print("ID da Máquina:", maquina[0],"- Sistema Operacional:", maquina[1],"- Endereço IP:",
              maquina[2],"- Sala:", maquina[3],"- Andar:", maquina[4], "- Setor:", maquina[5], "\n")

    # usuário escolhendo a máquina que quer monitorar
    idMaquinaSelect = input("Qual o ID da máquina que você quer monitorar?")
    query = "SELECT idMaquina FROM Maquina WHERE idMaquina = %s"
    cursor.execute(query, (idMaquinaSelect,))
    idMaquinaInsert = cursor.fetchone()

    # verificando se a máquina existe
    if idMaquinaInsert:
        print("Iniciando o Monitoramento")

        # Puxando a fkPlanoEmpresa
        query = "SELECT fkPlanoEmpresa FROM Maquina WHERE idMaquina = %s"
        cursor.execute(query, (idMaquinaSelect,))
        fkPlanoEmpresa = cursor.fetchone()

        # Puxando a fkTipoMaquina
        query = "SELECT fkTipoMaquina FROM Maquina WHERE idMaquina = %s"
        cursor.execute(query, (idMaquinaSelect,))
        fkTipoMaquina = cursor.fetchone()

        # puxando dados da máquina escolhida
        query = "select idMaquina, SO, IP, sala, andar, nome from Maquina JOIN LocalSala on fkLocal = idLocalSala join setor on fkSetor = idSetor WHERE idMaquina = %s;"
        cursor.execute(query, (idMaquinaSelect,))
        DadosMaquinas = cursor.fetchone()

        # rodando o monitoramento
        while True:
 uso_cpu = round(psutil.cpu_percent(interval=1), 2)
            uso_disco = round(psutil.disk_usage('/').percent, 2)
            uso_memoria = round(psutil.virtual_memory().percent, 2)
            data = datetime.datetime.now()


            webhook = "https://hooks.slack.com/services/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"

            if 15.0 <= uso_cpu < 30.0:
                alerta = {"text": f"Alerta! CPU com {uso_cpu}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}" }
                requests.post(webhook, data=json.dumps(alerta))
            elif uso_cpu >= 30.0:
                alerta = {"text": f"Crítico! CPU com {uso_cpu}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}"}
                requests.post(webhook, data=json.dumps(alerta))

            if 40.0 <= uso_memoria < 50.0:
                alerta = {"text": f"Alerta! RAM com {uso_memoria}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}"}
                requests.post(webhook, data=json.dumps(alerta))
            elif uso_memoria >= 50.0:
                alerta = {"text": f"Crítico! RAM com {uso_memoria}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}"}
                requests.post(webhook, data=json.dumps(alerta))

            if 65.0 <= uso_disco < 70.0:
                alerta = {"text": f"Alerta! Disco com {uso_disco}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}"}
                requests.post(webhook, data=json.dumps(alerta))
            elif uso_disco >= 70.0:
                alerta = {"text": f"Crítico! RAM com {uso_disco}% de uso, Maquina com o IP: {DadosMaquinas[2]}, andar: {DadosMaquinas[4]}, sala: {DadosMaquinas[3]}"}
                requests.post(webhook, data=json.dumps(alerta))



            #query = '''
            #insert into Monitoramento(porcentagem, dataHora, fkComponente, fkMaquina, fkPlanoEmpresa, fkTipoMaquina, fkEmpresaMaquina)
            #VALUES (%s, %s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s, %s), (%s, %s, %s, %s, %s, %s, %s);
            #'''
            #insert = [
                #uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0]
            #]

            #cursorSql = connectionSql.cursor()
  #cursorSql.execute(query, insert)
            #connectionSql.commit()




            query = '''
            insert into Monitoramento(porcentagem, dataHora, fkComponente, fkMaquina, fkPlanoEmpresa, fkTipoMaquina, fkEmpresaMaquina)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            '''

            queryServer = '''
            insert into Monitoramento(porcentagem, dataHora, fkComponente, fkMaquina, fkPlanoEmpresa, fkTipoMaquina, fkEmpresaMaquina)
            VALUES (%s, %s, %s, %s, %s, %s, %s);

            '''

            insert_values_cpu = (
                uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0]
            )

            insert_values_ram = (
                #uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0]
            )

            insert_values_disco = (
                #uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0]
            )



            insert_values_sql_server_cpu = (
                uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                # Adicione mais conjuntos de valores conforme necessário
   )

            insert_values_sql_server_ram = (
                #uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                # Adicione mais conjuntos de valores conforme necessário
            )

            insert_values_sql_server_disco = (
                #uso_cpu, data, 1, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                uso_disco, data, 2, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                #uso_memoria, data, 3, idMaquinaInsert[0], fkPlanoEmpresa[0], fkTipoMaquina[0], fkEmpresa[0],
                # Adicione mais conjuntos de valores conforme necessário
            )



            #print(insert_values, insert_values_sql_server)

            insert_data(sql_server_connection, queryServer, insert_values_sql_server_cpu)
            insert_data(sql_server_connection, queryServer, insert_values_sql_server_ram)
            insert_data(sql_server_connection, queryServer, insert_values_sql_server_disco)

            # Criar cursor
            cursor = connection.cursor()

            # Executar a query
            cursor.execute(query, insert_values_cpu)
            cursor.execute(query, insert_values_ram)
            cursor.execute(query, insert_values_disco)
            connection.commit()

            print(f"Uso da CPU: {uso_cpu}%")
            print(f"Uso do Disco: {uso_disco}%")
            print(f"Uso da Memória: {uso_memoria}%\r\n")

            time.sleep(5)
 else:
        print("Máquina não está cadastrada")

else:
    print("Login Inválido")
