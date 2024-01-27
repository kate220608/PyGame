import sqlite3


def add_score_to_bd(score):
    con = sqlite3.connect("result_base")
    cur = con.cursor()
    cur.execute("INSERT INTO results (score) VALUES (?)", (str(score), ))
    con.commit()
    con.close()


def find_best_score():
    con = sqlite3.connect("result_base")
    cur = con.cursor()
    res = cur.execute("SELECT score FROM results").fetchall()
    con.close()
    return max(res[1])
