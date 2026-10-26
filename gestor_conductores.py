import os
import json
import subprocess
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
import db
import config

BASE = os.path.dirname(os.path.abspath(__file__))
PY = r"F:\Desktop\.venv\Scripts\python.exe"


class Gestor(tk.Tk):
    def __init__(self):
        super().__init__()
        db.init()
        self.title("Gestor de Conductores")
        self.geometry("560x520")
        self.configure(padx=14, pady=14)

        ttk.Label(self, text="Nuevo conductor", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        f = ttk.Frame(self)
        f.pack(fill="x", pady=8)
        ttk.Label(f, text="Nombre:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_nombre = ttk.Entry(f, width=30)
        self.ent_nombre.grid(row=0, column=1, padx=8)
        ttk.Label(f, text="Contacto Telegram (chat_id):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_contacto = ttk.Entry(f, width=30)
        self.ent_contacto.grid(row=1, column=1, padx=8)

        r0 = ttk.Frame(self)
        r0.pack(anchor="w", pady=4)
        ttk.Button(r0, text="📷  Agregar y capturar rostro", command=self.agregar).pack(side="left")
        ttk.Button(r0, text="🔎 Obtener chat_id", command=self.obtener_chatid).pack(side="left", padx=6)
        ttk.Label(self, text="(Se abre la cámara; mové la cara y esperá a que junte las tomas)",
                  foreground="#666").pack(anchor="w")

        ttk.Separator(self).pack(fill="x", pady=12)
        ttk.Label(self, text="Conductores cargados", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.tree = ttk.Treeview(self, columns=("nombre", "contacto", "rostros"),
                                 show="headings", height=8)
        for col, txt, w in [("nombre", "Nombre", 180), ("contacto", "Contacto", 200), ("rostros", "Rostros", 80)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True, pady=6)

        r = ttk.Frame(self)
        r.pack(fill="x")
        ttk.Button(r, text="Actualizar lista", command=self.refrescar).pack(side="left")
        ttk.Button(r, text="Eliminar seleccionado", command=self.eliminar).pack(side="left", padx=6)
        ttk.Button(r, text="▶ Iniciar sistema", command=self.iniciar).pack(side="right")

        self.refrescar()

    def refrescar(self):
        self.tree.delete(*self.tree.get_children())
        for nombre, chat, n in db.listar():
            self.tree.insert("", "end", values=(nombre, chat or "-", n))

    def agregar(self):
        nombre = self.ent_nombre.get().strip().lower()
        contacto = self.ent_contacto.get().strip()
        if not nombre:
            messagebox.showwarning("Falta dato", "Escribí un nombre.")
            return
        subprocess.Popen([PY, "cargar_conductor.py", "--nombre", nombre, "--contacto", contacto],
                         cwd=BASE, creationflags=subprocess.CREATE_NEW_CONSOLE)
        messagebox.showinfo("Capturando",
                            "Se abrió la cámara para capturar el rostro.\n"
                            "Cuando termine, tocá 'Actualizar lista'.")

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            return
        nombre = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Eliminar", f"¿Eliminar a '{nombre}'?"):
            db.eliminar(str(nombre))
            self.refrescar()

    def obtener_chatid(self):
        if not config.TG_TOKEN:
            messagebox.showerror("Falta el token", "No esta configurada la variable de entorno TG_TOKEN.\n" "Ver el README PARA CONFIGURARLA")
            return
        try:
            url = f"https://api.telegram.org/bot{config.TG_TOKEN}/getUpdates"
            data = json.loads(urllib.request.urlopen(url, timeout=10).read().decode())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        ids = {}
        for u in data.get("result", []):
            m = u.get("message") or u.get("edited_message") or {}
            ch = m.get("chat", {})
            if ch:
                ids[ch.get("id")] = f"{ch.get('first_name', '')} {ch.get('last_name', '') or ''}".strip()
        if ids:
            txt = "\n".join(f"{k}   ({v})" for k, v in ids.items())
            messagebox.showinfo("Chat IDs disponibles",
                                txt + "\n\nCopiá el número en el campo 'Contacto Telegram'.")
        else:
            messagebox.showinfo("Sin datos",
                                "Nadie le escribió al bot todavía.\n"
                                "Pedile al contacto que le envíe /start a tu bot y reintentá.")

    def iniciar(self):
        subprocess.Popen([PY, "sistema.py"], cwd=BASE, creationflags=subprocess.CREATE_NEW_CONSOLE)


if __name__ == "__main__":
    Gestor().mainloop()
