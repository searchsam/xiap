# xiap

A lot of XARK in a little pond.

## Flask

Instalar flask

## PostgreSQL

```bash
$ sudo dnf -y install postgresql postgresql-server # instalar postgres
$ postgresql-setup --initdb # Iniciar el cluster
$ sudo systemctl start postgresql.service # Iniciar el motor como servicio
$ sudo systemctl enable postgresql  # Activar el inicio al arrancar el sistema
$ sudo su - postgres    # Carbiar a la consola del usuario postgres
$ psql  # Loguearse en la consola del servidor postgres
=# \password (Escribir la contraseña dos veces. `temporalmentepacapaca`) # Asignar contraseña al usuario postgres
=# \q
# =============================================================================
=# CREATE USER ponduser WITH PASSWORD 'xarktank';
=# GRANT ALL PRIVILEGES ON DATABASE xiap to ponduser;
=# CREATE DATABASE xiap WITH OWNER ponduser;
=# \q
# =============================================================================
$ createuser ponduser -P
$ createdb xiap --owner ponduser
CONFILE = $(psql -U postgres -c 'SHOW config_file')
$ sudo vim /etc/postgres/10/main/pg_hba.conf
    Cambiar:
    local   all    all                    peer
    host    all    all    127.0.0.1/32    peer
    Por:
    local   all    all                    md5
    host    all    all    0.0.0.0/0       md5

$ sudo vim /etc/postgres/10/main/postgres.conf    
    Cambiar:
    # listen_addresses = 'localhost'
    Por:
    listen_addresses = '*'

$ sudo systemctl restart postgresql
e8262ad87bde192dc6840b3caf1957b42282f6f8d20589e5e21949bb73ac5725
```

## Resources

- <https://pythontic.com/serialization/apache%20avro/write%20data>
- <https://github.com/Psalms23/rxpy-flask-api>
- <https://github.com/authlib/example-oauth2-server>
- <https://www.adictosaltrabajo.com/2012/07/30/spring-mvc-api-rest-oauth-2/>
