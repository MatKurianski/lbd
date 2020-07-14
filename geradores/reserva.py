import mysql.connector
import random
import datetime

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


def get_random_date():
  start_date = datetime.date(2020, 8, 1)

  end_date = datetime.date(2020, 12, 30)


  time_between_dates = end_date - start_date

  days_between_dates = time_between_dates.days

  random_number_of_days = random.randrange(days_between_dates)

  random_date = start_date + datetime.timedelta(days=random_number_of_days)

  return random_date.strftime("%Y-%m-%d")


class SocioDAO:
  def get_socios(self):
    mycursor.execute('SELECT idSocio, nome as id_socio FROM Socio')
    results = mycursor.fetchall()
    return [x[0] for x in results]

class SalaDAO:
  def get_numero_salas(self):
    mycursor.execute('SELECT numero FROM Sala WHERE tipo_sala = 2')
    salas = mycursor.fetchall()
    return [sala[0] for sala in salas]

def random_with_N_digits(n):
  range_start = 10**(n-1)
  range_end = (10**n)-1
  return random.randint(range_start, range_end)

salas = SalaDAO().get_numero_salas()

class ReservaDAO:
  def get_reservas_by_sala(self, sala, dia):
    sql = 'SELECT DATE_FORMAT(r.data_hora, "%H") as hora FROM Reserva r WHERE r.numero_sala = {0} AND r.data_hora >= "{1}" AND r.data_hora < DATE_ADD("{1}", INTERVAL 1 DAY);'.format(sala, dia)
    mycursor.execute(sql)
    _horarios = mycursor.fetchall()
    horarios = {int(horario[0]) for horario in _horarios}
    return horarios

socios = SocioDAO().get_socios()
date = get_random_date()

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

datas = [get_random_date() for x in range(1000)]

for sala in [random.choice(salas) for x in range(0,150)]:
  print("Sala {} escolhida!\n".format(sala))
  for data in datas:
    horarios_reservados = ReservaDAO().get_reservas_by_sala(sala, data)
    horarios_disp = {x for x in range(0,24)} - horarios_reservados

    sql = "INSERT IGNORE INTO Reserva (socio_id, numero_sala, data_hora) VALUES (%s, %s, %s)"
    _datas = [(random.choice(socios), sala, data + " {}:00:00".format(horario)) for horario in horarios_disp]
    print("{} criada!".format(str(data)))
    mycursor.executemany(sql, _datas)
    mydb.commit()
