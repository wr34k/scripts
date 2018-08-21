#!/usr/bin/env python3

import argparse
import psycopg2 as pg


def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("-H", "--host",help="Hostname or IP", default="localhost")
    p.add_argument("-p", "--port",help="Port of the service", default="5432")
    p.add_argument("-d", "--dbname",help="database to connect", default="postgres")
    p.add_argument("-U", "--user",help="Username to connect with", required=True)
    p.add_argument("-P", "--pass",help="Password to use", required=True)
    p.add_argument("-t", "--table", help="Table to delete dupes", required=True)
    p.add_argument("-w", "--where", help="Custom where clause")
    p.add_argument("--delete", help="Perform the deletion", action='store_true')

    return vars(p.parse_args())


def get_dupes_count_query(args, cols):
    dupes_count_query = "SELECT COUNT(*) FROM (SELECT "
    dupes_count_query += ", ".join(cols['name'])
    dupes_count_query += f", count(*) FROM {args['table']}"
    dupes_count_query += f" where {args['where']}" if args['where'] else ""
    dupes_count_query += " GROUP BY "
    dupes_count_query += ", ".join(cols['name'])
    dupes_count_query += " having count(*) > 1"
    dupes_count_query += ") A"
    return dupes_count_query


def gen_coal_values(cols):
    coal = []
    for i in range(len(cols['type'])):
        if cols['type'][i] in ('character varying', 'text'):
            coal += [f"COALESCE(a.{cols['name'][i]}, 'NULL')=COALESCE(b.{cols['name'][i]}, 'NULL')"]
        elif cols['type'][i] in ('timestamp', 'timestamp without time zone'):
            coal += [f"COALESCE(a.{cols['name'][i]}, '1970-01-01 00:00:00')=COALESCE(b.{cols['name'][i]}, '1970-01-01 00:00:00')"]
        elif cols['type'][i] in ('integer', 'double precision'):
            coal += [f"COALESCE(a.{cols['name'][i]}, -1)=COALESCE(b.{cols['name'][i]}, -1)"]
        else:
            coal += [f"COALESCE(a.{cols['name'][i]}, -1)=COALESCE(b.{cols['name'][i]}, -1)"]
    return coal


def get_del_query(args, cols):
    del_query = f"DELETE FROM {args['table']} a using (select min(ctid) as ctid, "
    del_query += ", ".join(cols['name'])
    del_query += f", count(*) from {args['table']} group by "
    del_query += ", ".join(cols['name'])
    del_query += " having count(*) > 1) b where "
    del_query += " and ".join(cols['coal'])
    del_query += " and a.ctid <> b.ctid"
    del_query += f" and a.{args['where']}" if args['where'] else ""
    return del_query


def main():
    args = get_args()

    conn = pg.connect(f"host={args['host']} port={args['port']} dbname={args['dbname']} user={args['user']} password={args['pass']}")
    cur = conn.cursor()
    schema,table  = args['table'].split(".")

    cur.execute(f"select data_type, column_name from information_schema.columns where table_schema = '{schema}' and table_name = '{table}'")
    tmp = cur.fetchall()

    cols = {}
    cols['type'] = [x[0] for x in tmp]
    cols['name'] = [x[1] for x in tmp]

    dupes_count_query = get_dupes_count_query(args, cols)
    cur.execute(dupes_count_query)
    total_dupes = [x[0] for x in cur.fetchall()][0]
    print(f"[*] Total dupes: {total_dupes}")

    if not args['delete']:
        return

    if total_dupes == 0:
        print("[!] No dupes to delete... Exiting...")
        return

    cols['coal'] = gen_coal_values(cols)

    del_query = get_del_query(args, cols)
    cur.execute(del_query)

    print("[+] Dupes deleted")

    cur.execute(dupes_count_query)
    total_dupes = [x[0] for x in cur.fetchall()][0]
    print(f"[*] Total dupes: {total_dupes}")

    user_input = input("Shall we commit? [Y/n]: ")

    if user_input.lower() == 'n':
        print("[*] Rollbacking ...")
        cur.execute("rollback")
        print("[+] Done!")
        return


    cur.execute("commit")
    print("[+] Commited!")


if __name__=='__main__':
    exit(main())
