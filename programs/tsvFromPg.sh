#!/bin/sh

DB="translatin_wemi"
SCHEMA="public"
USER="postgres"
DEST=~/local/translatin/metadata/tables

psql -U $USER -w -Atc "select tablename from pg_tables where schemaname='$SCHEMA'" $DB |\
  while read TBL; do
      psql -U $USER -w -c "COPY $SCHEMA.$TBL TO STDOUT WITH (FORCE_QUOTE *, DELIMITER E'\t', FORMAT CSV, HEADER)" $DB > $DEST/$TBL.tsv
  done
