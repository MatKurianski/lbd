-- NOTA: Usamos SQL_NO_CACHE para que o cache não atrapalhe nossas métricas

/* Nossa primeira modificação foi criar índices no nome dos Sócios, de modo que acelere a funcionalidade de busca por nome. 
 * 
 * A query e o desempenho original eram esses:
 * */

SELECT SQL_NO_CACHE * FROM Socio s Where nome LIKE "%Shakira%";
 -- Tempo de execução aproximado: 220ms

ALTER TABLE Socio DROP INDEX Socio_nome_IDX;

-- Criamos então o índice com o seguinte comando (Nota: não há índices HASH em MySQL, então não tínhamos tanta opção) 

CREATE INDEX Socio_nome_IDX USING BTREE ON academia.Socio (nome);

/* Além disso, a query original não tira proveito desses índices, pois o duplo % exige uma varredura total do banco de dados durante a consulta.
 * Substituiremos a query original pela abaixo, que embora agora faça com que a aplicação pesquise apenas por nomes que começam com o pesquisado,
 * traz ganhos de desempenho por fazer uso do índice criado.
 * */

SELECT SQL_NO_CACHE * FROM Socio s Where nome LIKE "Shakira%";
 -- Tempo de execução aproximado: 165ms
 

-- Outra coisa que aprimoramos é que tínhamos o seguinte trigger para evitar reservas no mesmo horário antes de cada inserção:
-- Nota: Nossa aplicação só permite reservas por hora, sem minutos/segundos quebrados.


CREATE OR REPLACE TRIGGER sem_duplicata BEFORE INSERT ON Reserva
FOR EACH ROW
BEGIN
	IF EXISTS(SELECT * FROM Reserva WHERE numero_sala = NEW.numero_sala AND HOUR(data_hora) = HOUR(NEW.data_hora) AND DATE(data_hora) = DATE(NEW.data_hora))
	THEN
	    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = "Já existe reserva nesse horário e dia";
	END IF;
END;

SELECT SQL_NO_CACHE * FROM Reserva WHERE numero_sala = 3 AND HOUR(data_hora) = HOUR("2023-02-08 05:00:00") AND DATE(data_hora) = DATE("2023-02-08 05:00:00");

SELECT * FROM Reserva WHERE numero_sala = NEW.numero_sala AND HOUR(data_hora) = HOUR(NEW.data_hora) AND DATE(data_hora) = DATE(NEW.data_hora);

-- Usar as funções HOUR e DATE no WHERE faz com que possíveis índices não seja aproveitados e para todo registro testado deve ser executada essas funções, trazendo um overhead significativo.
-- O mesmo ocorria com a consulta que verificava os horários ocupados na nossa aplicação:

SELECT * FROM Reserva WHERE numero_sala = NEW.numero_sala AND HOUR(data_hora) = HOUR(NEW.data_hora) AND DATE(data_hora) = DATE(NEW.data_hora)

SELECT SQL_NO_CACHE * FROM Reserva r WHERE DATE_FORMAT(r.data_hora, "%d/%m/%y") = "28/12/23";

-- Havíamos feito isso pois o formato que nossa aplicação trabalha com datas é %d/%m/%y e o banco %y-%m-%d.

-- Pois bem, agora criamos um índice para as datas:

CREATE INDEX Reserva_date_IDX USING BTREE ON academia.Reserva (data_hora);

-- Agora reconstruímos o Trigger, considerando usar os índices e usando a função HOUR só em registros seletos.

CREATE OR REPLACE TRIGGER sem_duplicata BEFORE INSERT ON Reserva
FOR EACH ROW
BEGIN
	IF EXISTS(SELECT data_hora FROM (SELECT data_hora FROM Reserva WHERE numero_sala = NEW.numero_sala AND data_hora >= NEW.data_hora AND data_hora < DATE_ADD(NEW.data_hora,INTERVAL 1 DAY)) t WHERE HOUR(data_hora) = HOUR(NEW.data_hora))
	THEN
	    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = "Já existe reserva nesse horário e dia";
	END IF;
END;

ALTER TABLE Reserva DROP INDEX Reserva_date_IDX;

SELECT SQL_NO_CACHE * FROM Reserva r WHERE data_hora = "2023-02-08 05:00:00";

SELECT SQL_NO_CACHE * FROM Reserva WHERE HOUR(data_hora) = HOUR("2023-02-08 05:00:00") AND DATE(data_hora) = DATE("2023-02-08 05:00:00");

SELECT SQL_NO_CACHE HOUR(data_hora) as hora FROM (SELECT * FROM Reserva WHERE data_hora >= "2023-02-08 05:00:00" AND data_hora <= DATE_ADD("2023-02-08 05:00:00",INTERVAL 1 DAY)) t WHERE HOUR(data_hora) = HOUR("2023-02-08 05:00:00");

SELECT SQL_NO_CACHE * FROM Reserva WHERE HOUR(data_hora) = HOUR("2023-02-08 05:00:00") AND DATE(data_hora) = DATE("2023-02-08 05:00:00");


-- Reconstruímos também a função que verifica horários reservados de determinada sala em determinado dia:

SELECT SQL_NO_CACHE data_hora FROM (SELECT data_hora FROM Reserva WHERE numero_sala = 1 AND data_hora >= "20/07/13" AND data_hora <= DATE_ADD("20/07/13",INTERVAL 1 DAY)) t WHERE HOUR(data_hora) = 0;


