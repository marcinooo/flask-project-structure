#!/bin/sh

DB_HOST=postgres
DB_PORT=5432

for count in {1..20}; do
    echo "Pinging mysql database attempt "${count}
    if  $(nc -z ${DB_HOST} ${DB_PORT}) ; then
        echo "Can connect into database"
        break
    fi
    sleep 5
done
