This is just a way to measure how people compare random country flags to each
other, with some ranking and statistics to come later.

This uses postgres as a backend, setup is simple, as the postgres user run
these commands under psql:

    CREATE USER flags WITH ENCRYPTED PASSWORD 'password';
    CREATE DATABASE flags OWNER flags;
    ALTER ROLE flags SET client_encoding TO 'utf8';
    ALTER ROLE flags SET default_transaction_isolation TO 'read committed';
    ALTER ROLE flags SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE flags TO flags;
