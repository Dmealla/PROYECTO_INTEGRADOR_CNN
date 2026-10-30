import os
import sqlite3
import numpy as np

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),"conductores.db")
TAM = 200


def _c():
    return sqlite3.connect(RUTA)


def init():
    c = _c()
    c.execute("CREATE TABLE IF NOT EXISTS conductores(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, chat_id TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS rostros(id INTEGER PRIMARY KEY AUTOINCREMENT, conductor_id INTEGER, img BLOB)")
    c.commit()
    c.close()


def agregar_conductor(nombre, chat_id):
    c = _c()
    cur = c.cursor()
    cur.execute("INSERT OR IGNORE INTO conductores(nombre, chat_id) VALUES(?,?)", (nombre, chat_id))
    cur.execute("UPDATE conductores SET chat_id=? WHERE nombre=?", (chat_id, nombre))
    c.commit()
    cur.execute("SELECT id FROM conductores WHERE nombre=?", (nombre,))
    cid = cur.fetchone()[0]
    c.close()
    return cid


def guardar_rostro(conductor_id, img):
    c = _c()
    c.execute("INSERT INTO rostros(conductor_id, img) VALUES(?,?)", (conductor_id, img.tobytes()))
    c.commit()
    c.close()


def datos_entrenamiento():
    c = _c()
    cur = c.cursor()
    cur.execute("SELECT conductor_id, img FROM rostros")
    caras, labels = [], []
    for cid, blob in cur.fetchall():
        caras.append(np.frombuffer(blob, dtype=np.uint8).reshape(TAM, TAM))
        labels.append(cid)
    cur.execute("SELECT id, nombre FROM conductores")
    nombres = {i: n for i, n in cur.fetchall()}
    c.close()
    return caras, labels, nombres


def chat_id(conductor_id):
    c = _c()
    cur = c.cursor()
    cur.execute("SELECT chat_id FROM conductores WHERE id=?", (conductor_id,))
    r = cur.fetchone()
    c.close()
    return r[0] if r else ""


def listar():
    c = _c()
    cur = c.cursor()
    cur.execute("SELECT c.nombre, c.chat_id, COUNT(r.id) FROM conductores c LEFT JOIN rostros r ON r.conductor_id=c.id GROUP BY c.id")
    r = cur.fetchall()
    c.close()
    return r


def eliminar(nombre):
    c = _c()
    cur = c.cursor()
    cur.execute("SELECT id FROM conductores WHERE nombre=?", (nombre,))
    r = cur.fetchone()
    if r:
        cur.execute("DELETE FROM rostros WHERE conductor_id=?", (r[0],))
        cur.execute("DELETE FROM conductores WHERE id=?", (r[0],))
        c.commit()
    c.close()
