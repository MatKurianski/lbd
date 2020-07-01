import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

import mysql.connector

mydb = mysql.connector.connect(
    host="academia.cdepsnadkn4y.us-east-1.rds.amazonaws.com",
    user="admin",
    database="academia",
    password="eacherifes"
)

mycursor = mydb.cursor()

## class MainWindow:
Ui_MainWindow, QtBaseClass = uic.loadUiType("mainwindow.ui")

class Socio:
    def __init__(self, id, nome):
        self.set_id(id)
        self.set_nome(nome)
  
    def get_id(self):
        return self.id
  
    def set_id(self, id):
        self.id = str(id)
  
    def get_nome(self):
        return self.nome

    def set_nome(self, nome):
        self.nome = str(nome)

class SocioDAO:
    def get_socios(self):
        mycursor.execute('SELECT idSocio, nome as id_socio FROM Socio')
        results = mycursor.fetchall()
        return [Socio(x[0],x[1]) for x in results]

class Sala:
    def __init__(self, numero_sala):
        self.set_numero_sala(numero_sala)

    def get_numero_sala(self):
        return self.numero_sala

    def set_numero_sala(self, numero_sala):
        self.numero_sala = str(numero_sala)

class SalaDAO:
    def get_numero_salas(self):
        mycursor.execute('SELECT numero FROM Sala WHERE tipo_sala = 2')
        salas = mycursor.fetchall()
        return [Sala(sala[0]) for sala in salas]

class Reserva:
    def __init__(self, id, id_socio, nome, numero_sala, horario):
        self.set_id(id)
        self.set_id_socio(id_socio)
        self.set_nome(nome)
        self.set_numero_sala(numero_sala)
        self.set_horario(horario)

    def get_id(self):
        return self.id

    def get_id_socio(self):
        return self.id_socio
    
    def get_nome(self):
        return self.nome

    def get_numero_sala(self):
        return self.numero_sala
    
    def get_horario(self):
        return self.horario

    def set_id(self,id):
        self.id = str(id)
    
    def set_id_socio(self, id_socio):
        self.id_socio = str(id_socio)
    
    def set_nome(self, nome):
        self.nome = str(nome)

    def set_numero_sala(self, numero_sala):
        self.numero_sala = str(numero_sala)
    
    def set_horario(self, horario):
        self.horario = str(horario)

class ReservaDAO:
    def get_reservas(self):
        mycursor.execute('SELECT r.idReserva, s.idSocio, s.nome , r.numero_sala , DATE_FORMAT(data_hora, \'%d/%m/%y %H:00\') as horario FROM Reserva r INNER JOIN Socio s ON r.socio_id = s.idSocio ORDER BY r.idReserva DESC LIMIT 100')
        _reservas = mycursor.fetchall()
        reservas = []
        for _reserva in _reservas:
            id, id_socio, nome, numero_sala, horario = _reserva
            reserva = Reserva(id, id_socio, nome, numero_sala, horario)
            reservas.append(reserva)
        return reservas

    def delete_reservas(self, ids):
        mycursor.execute('DELETE from Reserva WHERE idReserva IN '+ids)

    def get_by_nome_socio(self, name):
        mycursor.execute('SELECT r.idReserva, s.idSocio, s.nome , r.numero_sala , DATE_FORMAT(r.data_hora, \'%d/%m/%y %H:00\') as horario FROM Reserva r \
                            INNER JOIN Socio s ON r.socio_id = s.idSocio WHERE s.nome LIKE "{}%"'.format(name))
        _reservas = mycursor.fetchall()
        reservas = []
        for _reserva in _reservas:
            id, id_socio, nome, numero_sala, horario = _reserva
            reserva = Reserva(id, id_socio, nome, numero_sala, horario)
            reservas.append(reserva)
        return reservas

    def add_reserva(self, sala, socio, horario):
        try:
            mycursor.execute('INSERT INTO Reserva (idReserva, numero_sala, socio_id, data_hora) VALUES (NULL, {}, {}, "{}")'.format(sala, socio, horario))
            mydb.commit()
        except mysql.connector.Error as e:
            return False
        else:
            return True

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        loadUi('dialog.ui', self)
        self.horario_edit.setMinimumDate(QDate.currentDate().addDays(1))
        self.reserva_button.clicked.connect(self.submit)
        self.cancela_button.clicked.connect(self.close)

        self.selecionado_socio = None
        self.selecionada_sala = None

        _socios = SocioDAO().get_socios()
        socios = [(socio.get_id(),socio.get_nome()) for socio in _socios]
        self.socios = dict(socios)
        self.id_lineedit.textChanged.connect(self.changed_socio)

        _salas = SalaDAO().get_numero_salas()
        salas = [sala.get_numero_sala() for sala in _salas]

        if len(salas) > 0:
            self.selecionada_sala = salas[0]

        self.sala_combobox.addItems(salas)

    def submit(self):
        if self.selecionado_socio is None:
            QMessageBox.about(self, "Usuário Inválido", "Esse usuário não existe")
            return
        elif self.selecionada_sala is None:
            QMessageBox.about(self, "Sala Inválida", "Essa sala não existe")
            return
        _horario = self.horario_edit.dateTime()
        horario = _horario.toString(self.horario_edit.displayFormat()) + ":00"
        if ReservaDAO().add_reserva(self.selecionada_sala, self.selecionado_socio, horario):
            self.done(0)
        else:
            QMessageBox.about(self, "Sala ocupada!", "Sala ocupada! Por favor, escolha outra sala ou outro horário")

    def changed_socio(self):
        id = self.id_lineedit.text()
        if id in self.socios:
            self.selecionado_socio = id
            self.selecionado.setText("Selecionado: {}".format(self.socios[id]))
        else:
            self.selecionado_socio = None
            self.selecionado.setText("Usuário não encontrado")
    
    def changed_sala(self, sala):
        self.selecionada_sala = sala

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle("Academia Sempre em Forma")
        self.socios_tabela.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.adiciona_button.clicked.connect(self.open_dialog)
        self.remove_button.clicked.connect(self.remove)
        self.pesquisa_button.clicked.connect(self.search_name)
        self.limpa_button.clicked.connect(self.clear)

        self.pesquisa = None

        header = self.socios_tabela.horizontalHeader()
        self.socios_tabela.setColumnHidden(0, True)      
        self.query_results()
    
    def query_results(self):
        self.toggle_buttons(False)
        if self.pesquisa is None or self.pesquisa == "":
            self.data = ReservaDAO().get_reservas()
        else:
            self.data = ReservaDAO().get_by_nome_socio(self.pesquisa)
        self.render_data()
        self.toggle_buttons(True)

    def search_name(self):
        self.pesquisa = self.pesquisa_lineedit.text()
        self.query_results()
    
    def toggle_buttons(self, toggle):
        self.pesquisa_button.setEnabled(toggle)
        self.remove_button.setEnabled(toggle)
        self.adiciona_button.setEnabled(toggle)
        self.limpa_button.setEnabled(toggle)

    def render_data(self):
        self.socios_tabela.setRowCount(0)
        for i, reserva in enumerate(self.data):
            self.socios_tabela.insertRow(i)
            
            self.socios_tabela.setItem(i, 0, QTableWidgetItem(reserva.get_id()))
            self.socios_tabela.setItem(i, 1, QTableWidgetItem(reserva.get_id_socio()))
            self.socios_tabela.setItem(i, 2, QTableWidgetItem(reserva.get_nome()))
            self.socios_tabela.setItem(i, 3, QTableWidgetItem(reserva.get_numero_sala()))
            self.socios_tabela.setItem(i, 4, QTableWidgetItem(reserva.get_horario()))
            

    def open_dialog(self):
        d = Dialog()
        d.exec_()
        self.query_results()
    
    def clear(self):
        self.pesquisa = None
        self.pesquisa_lineedit.setText("")
        self.query_results()

    def remove(self):
        indexes = self.socios_tabela.selectionModel().selectedRows()
        if len(indexes) > 0:
          _ids = {self.socios_tabela.item(x.row(), 0).text() for x in sorted(indexes)}
          ids = "({})".format(",".join(_ids))
          ReservaDAO().delete_reservas(ids)
          self.query_results()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())