import sqlite3


# %%

class DBHelper:
    def __init__(self, dbname=r'bot_db.db'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt_codes = """
        CREATE TABLE IF NOT EXISTS codes (
            rec_id INTEGER PRIMARY KEY,
            rec_timestamp TEXT NOT NULL,
            chat_id INTEGER NOT NULL,
            code TEXT NOT NULL); """
        codes_idx_code = """
        CREATE INDEX IF NOT EXISTS itemIndex
        ON codes (code ASC);"""
        codes_idx_chat = """
        CREATE INDEX IF NOT EXISTS ownIndex
        ON codes (chat_id);"""
        self.conn.execute(stmt_codes)
        self.conn.execute(codes_idx_code)
        self.conn.execute(codes_idx_chat)
        self.conn.commit()

    def add_code(self, chat_id, code):
        stmt = """
        INSERT INTO codes (rec_timestamp,
                           chat_id,
                           code)
        VALUES (datetime('now'), ?, ?); """
        args = (chat_id, code)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def del_code(self, chat_id, code):
        stmt = """
        DELETE FROM codes
        WHERE chat_id = (?) AND code = (?); """
        args = (chat_id, code)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_codes(self, chat_id):
        stmt = """
        SELECT code FROM codes
        WHERE chat_id = (?); """
        args = (chat_id, )
        return [str(x[0]) for x in self.conn.execute(stmt, args)]
