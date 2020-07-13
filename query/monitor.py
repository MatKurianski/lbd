import mysql.connector
import random

mydb = mysql.connector.connect(
    host="academia.cdepsnadkn4y.us-east-1.rds.amazonaws.com",
    user="admin",
    database="academia",
    password="eacherifes"
)

mycursor = mydb.cursor()

consoantes = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'x']

vogais = ['a', 'e', 'i', 'o', 'u']

profissoes = ['Dançarinah', 'Professorah', 'Historiadorah', 'Pintorah', "Arquitera"]

def random_with_N_digits(n):
  range_start = 10**(n-1)
  range_end = (10**n)-1
  return random.randint(range_start, range_end)

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

array = []
for i in range(100000):
  acc = ""
  for i in range(5):
    consoante = random.choice(consoantes)
    vogal = random.choice(vogais)
    silaba = consoante + vogal
    if i == 0:
      silaba = silaba.capitalize()
    acc += silaba
    
    if random.random() < 0.2:
      break

  
  acc += " "
  for i in range(5):
    consoante = random.choice(consoantes)
    vogal = random.choice(vogais)
    silaba = consoante + vogal
    if i == 0:
      silaba = silaba.capitalize()
    acc += silaba
    if random.random() < 0.2:
      break

  acc = (acc, random.choice(profissoes), acc[::-1] + ', ' + str(random_with_N_digits(3)), random_with_N_digits(9), 'NENHUM')
  array.append(acc)

for i, chunk in enumerate(chunks(array, 1000)):
  sql = "INSERT INTO Socio (nome, profissao, endereco, telefone, dados_bancarios) VALUES (%s, %s, %s, %s, %s)"
  val = chunk

  mycursor.executemany(sql, val)

  mydb.commit()

  print("Chunk {}: {} was inserted.".format(i, mycursor.rowcount)) 
