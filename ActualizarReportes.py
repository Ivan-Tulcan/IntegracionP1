import sqlite3
import csv
import os
import shutil
import tkinter as tk
from tkinter import messagebox, Listbox, END, Scrollbar, RIGHT, Y

# Configuración de la base de datos BDDNuevoSistema
conn = sqlite3.connect("BDDNuevoSistema.sqlite")
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

# Función para cargar archivos en las listas de la GUI
def cargar_listas():
    lista_reportes.delete(0, END)
    lista_respaldos.delete(0, END)
    
    # Cargar archivos de Reportes
    for archivo in os.listdir("Reportes"):
        if archivo.endswith(".csv"):
            lista_reportes.insert(END, archivo)
    
    # Cargar archivos de Respaldos
    for archivo in os.listdir("Respaldos"):
        if archivo.endswith(".csv"):
            lista_respaldos.insert(END, archivo)

# Función para copiar el archivo seleccionado
def copiar_reporte():
    seleccionado = lista_reportes.get(lista_reportes.curselection())
    mes, año = map(int, seleccionado.replace("Rep-", "").replace(".csv", "").split("-"))

    # Eliminar registros del mismo mes y año en la base de datos
    cursor.execute("DELETE FROM Registros WHERE mesReporte = ? AND añoReporte = ?", (mes, año))
    conn.commit()

    # Leer el archivo y copiar registros a la base de datos
    with open(f"Reportes/{seleccionado}", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("INSERT INTO Registros (fecha, mesReporte, añoReporte, tipoRegistro, monto) VALUES (?, ?, ?, ?, ?)",
                           (row['Fecha'], int(row['MesReporte']), int(row['AñoReporte']), row['TipoRegistro'], float(row['Monto'])))
    conn.commit()

    # Copiar el archivo a la carpeta Respaldos
    shutil.copy(f"Reportes/{seleccionado}", f"Respaldos/{seleccionado}")

    messagebox.showinfo("Copia Completa", f"El archivo {seleccionado} fue copiado a la carpeta Respaldos y sus registros fueron guardados en la base de datos.")
    cargar_listas()  # Actualizar las listas

# Función para mostrar todos los registros en la base de datos
def mostrar_registros():
    cursor.execute("SELECT * FROM Registros")
    registros = cursor.fetchall()
    registro_text.delete(1.0, END)
    
    if registros:
        for registro in registros:
            registro_text.insert(END, f"{registro}\n")
    else:
        registro_text.insert(END, "No hay registros en la base de datos.")

# Crear la carpeta Respaldos si no existe
os.makedirs("Respaldos", exist_ok=True)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Actualizar Reportes")

# Listbox para archivos en Reportes
tk.Label(root, text="Reportes").grid(row=0, column=0, padx=10, pady=5)
lista_reportes = Listbox(root, selectmode=tk.SINGLE)
lista_reportes.grid(row=1, column=0, padx=10, pady=5)

# Listbox para archivos en Respaldos
tk.Label(root, text="Respaldos").grid(row=0, column=1, padx=10, pady=5)
lista_respaldos = Listbox(root, selectmode=tk.SINGLE)
lista_respaldos.grid(row=1, column=1, padx=10, pady=5)

# Botón de Copiar
tk.Button(root, text="Copiar", command=copiar_reporte).grid(row=2, column=0, padx=10, pady=5)

# Botón para mostrar registros
tk.Button(root, text="Mostrar Registros", command=mostrar_registros).grid(row=2, column=1, padx=10, pady=5)

# Área de texto para mostrar registros
registro_text = tk.Text(root, height=10, width=50)
registro_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

# Barra de desplazamiento para el área de texto
scrollbar = Scrollbar(root, command=registro_text.yview)
scrollbar.grid(row=3, column=2, sticky='ns')
registro_text.config(yscrollcommand=scrollbar.set)

# Cargar listas al iniciar
cargar_listas()

root.mainloop()

# Cerrar la conexión al salir
conn.close()
