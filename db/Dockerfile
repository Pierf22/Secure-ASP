# Usa l'immagine ufficiale di MariaDB come base
FROM mariadb:latest

# Copia il dump del database nella directory di lavoro del container
COPY ./dump.sql /docker-entrypoint-initdb.d/

# La cartella /docker-entrypoint-initdb.d/ è utilizzata automaticamente da MariaDB
# per eseguire script SQL all'inizializzazione del database.

# Imposta una variabile d'ambiente per la password dell'utente root
ENV MYSQL_ROOT_PASSWORD=maria-pass
ENV MYSQL_DATABASE=secure-asp

# Espone la porta 3306 per permettere l'accesso al database
EXPOSE 3306

