import sqlite3
import csv
import random
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox

# Conexión a la base de datos
conn = sqlite3.connect("BDDNuevoSistema.sqlite")
cursor = conn.cursor()

# Crear carpeta ReportesTemporales si no existe
os.makedirs("ReportesTemporales", exist_ok=True)

# Función para generar un código único hexadecimal de 5 dígitos
def generar_codigo_hex():
    return f"{random.randint(0, 0xFFFFF):05X}"

# Función para generar el histórico en CSV
def generar_historico(fecha_inicio, fecha_fin):
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Las fechas deben estar en formato YYYY-MM-DD.")
        return

    # Consulta para obtener registros dentro del rango de fechas
    cursor.execute("SELECT * FROM Registros WHERE fecha BETWEEN ? AND ?", (fecha_inicio, fecha_fin))
    registros = cursor.fetchall()

    if not registros:
        messagebox.showinfo("Histórico", "No se encontraron registros dentro del rango de fechas seleccionado.")
        return

    # Nombre del archivo con un código único
    codigo_hex = generar_codigo_hex()
    nombre_reporte = f"ReportesTemporales/Reporte_{codigo_hex}.csv"

    # Escribir registros en el archivo .csv
    with open(nombre_reporte, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Fecha', 'MesReporte', 'AñoReporte', 'TipoRegistro', 'Monto'])  # Cabecera del archivo CSV
        writer.writerows(registros)

    messagebox.showinfo("Histórico Generado", f"Reporte generado: {nombre_reporte}")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Generar Histórico")

# Campos de entrada para rango de fechas
tk.Label(root, text="Fecha inicio (YYYY-MM-DD):").pack()
fecha_inicio_entry = tk.Entry(root)
fecha_inicio_entry.pack()

tk.Label(root, text="Fecha fin (YYYY-MM-DD):").pack()
fecha_fin_entry = tk.Entry(root)
fecha_fin_entry.pack()

# Botón para generar histórico
tk.Button(root, text="Generar Histórico", command=lambda: generar_historico(fecha_inicio_entry.get(), fecha_fin_entry.get())).pack()

root.mainloop()

# Cerrar la conexión al salir
conn.close()
