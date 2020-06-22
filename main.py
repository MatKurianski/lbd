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
    @staticmethod
    def get_all_ids():
        mycursor.execute('SELECT idSocio, nome as id_socio FROM Socio')
        results = mycursor.fetchall()
        return [str(x[0]) for x in results], [str(x[1]) for x in results]

class Reserva:
    def __init__(self):
        pass

    @staticmethod
    def get_all():
        mycursor.execute('SELECT r.idReserva, s.idSocio, s.nome , r.numero_sala , DATE_FORMAT(data_hora, \'%d/%m/%y %h:00\') as horario FROM Reserva r INNER JOIN Socio s ON r.socio_id = s.idSocio ORDER BY r.data_hora DESC LIMIT 100')
        results = mycursor.fetchall()
        return results

    @staticmethod
    def remove(ids):
        mycursor.execute('DELETE from Reserva WHERE idReserva IN '+ids)

    @staticmethod
    def get_by_name(name):
        mycursor.execute('SELECT r.idReserva, s.idSocio, s.nome , r.numero_sala , DATE_FORMAT(r.data_hora, \'%d/%m/%y %h:00\') as horario FROM Reserva r \
                            INNER JOIN Socio s ON r.socio_id = s.idSocio WHERE s.nome LIKE "%{}%"'.format(name))
        results = mycursor.fetchall()
        return results

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        loadUi('dialog.ui', self)
        self.dateTimeEdit.setMinimumDate(QDate.currentDate().addDays(1))
        self.reserva_button.clicked.connect(self.submit)
        self.cancela_button.clicked.connect(self.close)

        self.selecionado_value = None

        socios = Socio.get_all_ids()
        self.socios = dict(zip(socios[0], socios[1]))
        self.id_lineedit.textChanged.connect(self.changed_ids)

    def submit(self):
        if self.selecionado_value is None:
            QMessageBox.about(self, "Usuário Inválido", "Esse usuário não existe")
        print('salve')

    def changed_ids(self):
        id = self.id_lineedit.text()
        if id in self.socios:
            self.selecionado_value = id
            self.selecionado.setText("Selecionado: {}".format(self.socios[id]))
        else:
            self.selecionado_value = None
            self.selecionado.setText("Usuário não encontrado")
        

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
        if self.pesquisa is None:
            self.data = Reserva.get_all()
        else:
            self.data = Reserva.get_by_name(self.pesquisa)
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
        for i, x in enumerate(self.data):
            self.socios_tabela.insertRow(i)
            for j in range(len(x)):
                self.socios_tabela.setItem(i, j, QTableWidgetItem(str(x[j])))

    def open_dialog(self):
        d = Dialog()
        d.exec_()
    
    def clear(self):
        self.pesquisa = None
        self.pesquisa_lineedit.setText("")
        self.query_results()

    def remove(self):
        indexes = self.socios_tabela.selectionModel().selectedRows()
        _ids = {self.socios_tabela.item(x.row(), 0).text() for x in sorted(indexes)}
        ids = "({})".format(",".join(_ids))
        Reserva.remove(ids)
        self.query_results()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())