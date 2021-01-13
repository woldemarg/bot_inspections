import os  # heroku
import psycopg2


# %%

DATABASE_URL = os.environ['DATABASE_URL']  # heroku


# %%

class DBHelper:
    def __init__(self):
        # local development
        # self.conn = psycopg2.connect(
        #     host='db',  # '127.0.0.1'
        #     # port=5432,
        #     database='postgres',
        #     user='postgres',
        #     password=''  # 'pass'
        # )
        # heroku
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.conn.autocommit = True

    def setup(self):
        stmt_codes = """
        CREATE TABLE IF NOT EXISTS codes (
            rec_id SERIAL PRIMARY KEY,
            chat INTEGER NOT NULL,
            date TIMESTAMP NOT NULL,
            code INTEGER NOT NULL); """
        codes_idx_code = """
        CREATE INDEX IF NOT EXISTS itemIndex
        ON codes (code ASC);"""
        codes_idx_chat = """
        CREATE INDEX IF NOT EXISTS ownIndex
        ON codes (chat);"""
        self.conn.cursor().execute(stmt_codes)
        self.conn.cursor().execute(codes_idx_code)
        self.conn.cursor().execute(codes_idx_chat)
        self.conn.commit()

    def add_code(self, chat_id, code):
        stmt = """
        INSERT INTO codes (rec_id,
                           chat,
                           date,
                           code)
        VALUES (DEFAULT, %s, NOW(), %s); """
        args = (chat_id, code)
        self.conn.cursor().execute(stmt, args)
        self.conn.commit()

    def del_code(self, chat_id, code):
        stmt = """
        DELETE FROM codes
        WHERE chat = (%s) AND code = (%s); """
        args = (chat_id, code)
        self.conn.cursor().execute(stmt, args)
        self.conn.commit()

    def get_codes(self, chat_id):
        stmt = """
        SELECT code FROM codes
        WHERE chat = (%s); """
        args = (chat_id, )
        cursor = self.conn.cursor()
        cursor.execute(stmt, args)
        return [str(x[0]) for x in cursor.fetchall()]
