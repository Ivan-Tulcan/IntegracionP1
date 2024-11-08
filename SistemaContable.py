import sqlite3
import csv
import random
from datetime import datetime, timedelta
import os
import tkinter as tk
from tkinter import messagebox, filedialog

# Conexión a la base de datos
conn = sqlite3.connect("BDDLegacy.sqlite")
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS Registros (
    fecha TEXT,
    mesReporte INTEGER,
    añoReporte INTEGER,
    tipoRegistro TEXT CHECK(tipoRegistro IN ('ingreso', 'egreso')),
    monto REAL
)
''')
conn.commit()

# Función para guardar un registro manualmente
def guardar_registro(fecha, tipo, monto):
    mesReporte = int(fecha.split('-')[1])
    añoReporte = int(fecha.split('-')[0])
    cursor.execute("INSERT INTO Registros (fecha, mesReporte, añoReporte, tipoRegistro, monto) VALUES (?, ?, ?, ?, ?)",
                   (fecha, mesReporte, añoReporte, tipo, monto))
    conn.commit()
    messagebox.showinfo("Registro", "Registro guardado exitosamente.")

# Función para generar registros aleatorios
def generar_registros_aleatorios(cantidad, monto_min, monto_max, fecha_inicio, fecha_fin):
    registros_generados = []
    
    for _ in range(cantidad):
        fecha_random = fecha_inicio + timedelta(days=random.randint(0, (fecha_fin - fecha_inicio).days))
        tipo_random = random.choice(['ingreso', 'egreso'])
        monto_random = round(random.uniform(monto_min, monto_max), 2)
        
        # Guardar en una lista para insertar en lote
        registros_generados.append((fecha_random.strftime('%Y-%m-%d'), 
                                    int(fecha_random.strftime('%m')), 
                                    int(fecha_random.strftime('%Y')), 
                                    tipo_random, 
                                    monto_random))
    
    # Insertar todos los registros en la base de datos en una sola operación
    cursor.executemany("INSERT INTO Registros (fecha, mesReporte, añoReporte, tipoRegistro, monto) VALUES (?, ?, ?, ?, ?)", registros_generados)
    conn.commit()
    
    # Notificación al final
    messagebox.showinfo("Registros Aleatorios", f"{cantidad} registros generados exitosamente.")

# Función para generar el reporte .csv
def generar_reporte(mes, año):
    cursor.execute("SELECT * FROM Registros WHERE mesReporte = ? AND añoReporte = ?", (mes, año))
    registros = cursor.fetchall()

    if not registros:
        messagebox.showinfo("Reporte", "No se encontraron registros para el mes y año seleccionados.")
        return
    
    # Crear la carpeta si no existe
    os.makedirs("Reportes", exist_ok=True)
    nombre_reporte = f"Reportes/Rep-{mes}-{año}.csv"

    # Escribir en el archivo .csv
    with open(nombre_reporte, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Fecha', 'MesReporte', 'AñoReporte', 'TipoRegistro', 'Monto'])
        writer.writerows(registros)

    messagebox.showinfo("Reporte", f"Reporte generado: {nombre_reporte}")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Sistema Contable")

# Widgets para registro manual
tk.Label(root, text="Fecha (YYYY-MM-DD):").pack()
fecha_entry = tk.Entry(root)
fecha_entry.pack()

tk.Label(root, text="Tipo (ingreso/egreso):").pack()
tipo_entry = tk.Entry(root)
tipo_entry.pack()

tk.Label(root, text="Monto:").pack()
monto_entry = tk.Entry(root)
monto_entry.pack()

tk.Button(root, text="Guardar Registro", command=lambda: guardar_registro(fecha_entry.get(), tipo_entry.get(), float(monto_entry.get()))).pack()

# Widgets para generación de registros aleatorios
tk.Label(root, text="Cantidad de registros:").pack()
cantidad_entry = tk.Entry(root)
cantidad_entry.pack()

tk.Label(root, text="Monto mínimo:").pack()
monto_min_entry = tk.Entry(root)
monto_min_entry.pack()

tk.Label(root, text="Monto máximo:").pack()
monto_max_entry = tk.Entry(root)
monto_max_entry.pack()

tk.Label(root, text="Fecha inicio (YYYY-MM-DD):").pack()
fecha_inicio_entry = tk.Entry(root)
fecha_inicio_entry.pack()

tk.Label(root, text="Fecha fin (YYYY-MM-DD):").pack()
fecha_fin_entry = tk.Entry(root)
fecha_fin_entry.pack()

tk.Button(root, text="Generar Registros Aleatorios", command=lambda: generar_registros_aleatorios(int(cantidad_entry.get()), float(monto_min_entry.get()), float(monto_max_entry.get()), datetime.strptime(fecha_inicio_entry.get(), '%Y-%m-%d'), datetime.strptime(fecha_fin_entry.get(), '%Y-%m-%d'))).pack()

# Widgets para generación de reportes
tk.Label(root, text="Mes de reporte:").pack()
mes_entry = tk.Entry(root)
mes_entry.pack()

tk.Label(root, text="Año de reporte:").pack()
año_entry = tk.Entry(root)
año_entry.pack()

tk.Button(root, text="Generar Reporte", command=lambda: generar_reporte(int(mes_entry.get()), int(año_entry.get()))).pack()

root.mainloop()

# Cerrar la conexión al cerrar el programa
root.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), root.destroy()))
root.mainloop()
