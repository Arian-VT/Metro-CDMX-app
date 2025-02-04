#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:10:01 2024

Autores: 
    Jessica Mariana Monroy Mejía
    Aaron Jair Romero Solís
    Arián Villalba Tapia
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





""" Funciones de la app """    
def actualizar_estructura_datos():
    global elec, nodos, conec, estaciones_mostrar

    # Restaurar los datos originales antes de filtrar
    elec = elec_original.copy()
    nodos = nodos_original.copy()
    conec = conec_original.copy()

    # Eliminar estaciones inhabilitadas
    elec = {est: val for est, val in elec.items() if est not in estaciones_inhabilitadas}
    
    # Actualizar nodos
    nodos = {val: coord for est, val in elec_original.items() if est not in estaciones_inhabilitadas 
             for val, coord in [(elec_original[est], nodos_original[elec_original[est]])] }
    
    # Actualizar conexiones
    conec_nuevo = []
    for conexion in conec_original:
        # Verificar que ambos nodos de la conexión existan en los nodos actualizados
        if conexion[0] in nodos and conexion[1] in nodos:
            conec_nuevo.append(conexion)
    
    conec = conec_nuevo
    
    # Actualizar estaciones para mostrar
    estaciones_mostrar = tuple(elec.keys())

def mostrar_imagen():
    ventana_img = tk.Toplevel()
    ventana_img.title("Mapa del metro")
    ventana_img.config(background='black')
    
    image = Image.open('metro.png')
    resize_image = image.resize((500,700))
    img = ImageTk.PhotoImage(resize_image)
    imagen_pos = ttk.Label(ventana_img,image = img)
    imagen_pos.image = img
    imagen_pos.pack(pady = 20)
    boton_cerrar = ttk.Button(ventana_img, text = 'cerrar',
                              command = ventana_img.destroy)
    boton_cerrar.pack(pady = 10)

def on_select_inicio(event):
    global selec_inicio
    seleccion = event.widget.curselection()
    if seleccion:
        selec_inicio_1 = event.widget.get(seleccion[0])
        selec_inicio = elec[selec_inicio_1]
        actualizar_lista_destino(selec_inicio_1)

def on_select_fin(event):
    global selec_fin
    seleccion = event.widget.curselection()
    if seleccion:
        selec_fin1 = event.widget.get(seleccion[0])
        selec_fin = elec[selec_fin1]

def actualizar_lista_destino(selec_inicio):
    lista_destino.delete(0, tk.END)
    for estacion in estaciones_mostrar:
        if estacion != selec_inicio:
            lista_destino.insert(tk.END, estacion)

def inhabilitadas():
    ventana_des = tk.Toplevel()
    ventana_des.title("Estaciones saturadas")
    ventana_des.config(background='black')
    
    def aplicar_inhabilitadas():
        global estaciones_inhabilitadas
        seleccionadas = [lista_des.get(i) for i in lista_des.curselection()]
        estaciones_inhabilitadas = set(seleccionadas)
        
        # Actualizar las estructuras de datos
        actualizar_estructura_datos()
        
        # Reiniciar las listas de inicio y destino
        lista_inicio.delete(0, tk.END)
        lista_inicio.insert(tk.END, *estaciones_mostrar)
        lista_destino.delete(0, tk.END)
        
        ventana_des.destroy()

    lista_des = tk.Listbox(ventana_des, selectmode=tk.MULTIPLE)
    lista_des.insert(tk.END, *estaciones_mostrar)
    lista_des.pack()

    boton_aplicar = ttk.Button(ventana_des, text='Aplicar', command=aplicar_inhabilitadas)
    boton_aplicar.pack(pady=10)

def calcular_ruta():
    if selec_inicio is not None and selec_fin is not None:
        mejor_camino, mejor_longitud = ACO(selec_inicio, selec_fin)
        if mejor_camino:
            # Convertir números de estaciones a nombres
            nombres_estaciones = [list(elec.keys())[list(elec.values()).index(i)] for i in mejor_camino]
            etiqueta_camino.config(text=f"Ruta: {' → '.join(nombres_estaciones)}\nDistancia: {mejor_longitud:.4f}")
            
           
            visualizar_ruta(mejor_camino, estaciones_inhabilitadas)
        else:
            etiqueta_camino.config(text="No se encontró una ruta válida")
    else:
        etiqueta_camino.config(text="Por favor seleccione inicio y destino")

def visualizar_ruta(mejor_camino, estaciones_inhabilitadas):
    # Crear una nueva ventana para la visualización
    ventana_grafico = tk.Toplevel()
    ventana_grafico.title("Ruta del Metro")
    
    # Crear una figura de matplotlib
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    # Dibujar todos los nodos
    for nodo, (x, y) in nodos.items():
        # Determinar el color del nodo
        color = 'red' if list(elec.keys())[list(elec.values()).index(nodo)] in estaciones_inhabilitadas else 'blue'
        ax.scatter(y, x, color=color, s=100, zorder=3)
        
        # Añadir etiquetas de estaciones
        nombre_estacion = list(elec.keys())[list(elec.values()).index(nodo)]
        ax.annotate(nombre_estacion, (y, x), xytext=(5, 5), 
                    textcoords='offset points', fontsize=8, 
                    color='black', fontweight='bold')
    
    # Dibujar todas las conexiones en negro
    for (nodo1, nodo2) in conec:
        x1, y1 = nodos[nodo1]
        x2, y2 = nodos[nodo2]
        ax.plot([y1, y2], [x1, x2], color='black', linewidth=1, zorder=1)
    
    # Dibujar el camino encontrado en verde
    if mejor_camino:
        camino_x = [nodos[nodo][0] for nodo in mejor_camino]
        camino_y = [nodos[nodo][1] for nodo in mejor_camino]
        ax.plot(camino_y, camino_x, color='green', linewidth=4, zorder=2)
    
    # Configurar el gráfico
    ax.set_title("Ruta del Metro", fontsize=15, fontweight='bold')
    ax.set_xlabel("Longitud", fontsize=10)
    ax.set_ylabel("Latitud", fontsize=10)
    
    # Crear el canvas de Tkinter para mostrar la figura de matplotlib
    canvas = FigureCanvasTkAgg(fig, master=ventana_grafico)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    # Añadir un botón para cerrar la ventana
    boton_cerrar = ttk.Button(ventana_grafico, text='Cerrar', 
                               command=ventana_grafico.destroy)
    boton_cerrar.pack(pady=10)

def restaurar_estaciones():
    global estaciones_inhabilitadas
    estaciones_inhabilitadas.clear()
    actualizar_estructura_datos()
    
    # Reiniciar las listas de inicio y destino
    lista_inicio.delete(0, tk.END)
    lista_inicio.insert(tk.END, *estaciones_mostrar)
    lista_destino.delete(0, tk.END)

""" Funciones de ACO """
elec = {'Tacubaya' : 0,
              'Balderas':1,
              'Salto del Agua':2,
              'Pino Suárez':3,
              'Candelaria':4,
              'San Lázaro':5,
              'Pantitlán':6,
              'Tacuba':7,
              'Hidalgo':8,
              'Bellas Artes':9,
              'Chabacano':10,
              'Ermita':11,
              'Deportivo 18 de Marzo':12,
              'La Raza':13,
              'Guerrero':14,
              'Centro Médico':15,
              'Zapata':16,
              'Martin Carrera':17,
              'Consulado':18,
              'Morelos':19,
              'Jamaica':20,
              'Santa Anita':21,
              'Instituto del Petróleo':22,
              'Oceanía':23,
              'Rosario':24,
              'Mixcoac':25,
              'Garibaldi/Lagunilla':26,
              'Atlalilco':27
        }

nodos = {0:(19.402345454783276, -99.18754650844504),
              1:(19.426851852049396, -99.14895320838629),
              2:(19.427779735916953, -99.14352242373153),
              3:(19.4250687646928, -99.13296172769724),
              4:(19.430470548418132, -99.12078132028054),
              5:(19.43144185281738, -99.11412944189871),
              6:(19.41536167116546, -99.07425734677584),
              7:(19.46013359190713, -99.18727942526353),
              8:(19.438135461211527, -99.14728042265534),
              9:(19.436542583498802, -99.1416100225585),
              10:(19.409227480756844, -99.13561788773431),
              11:(19.362090778868936, -99.14259331289361),
              12:(19.48545753688918, -99.12553088058037),
              13:(19.470077384953125, -99.13652716462026),
              14:(19.445843757521434, -99.14524879009926),
              15:(19.407451576364902, -99.15507298166985),
              16:(19.37145259090591, -99.16508032375441),
              17:(19.48311260045865, -99.1069323652357),
              18:(19.458143743777214, -99.11390227006825),
              19:(19.439969559942103, -99.11777008217139),
              20:(19.4122270113133, -99.1216370202885),
              21:(19.40517312667265, -99.12105630443082),
              22:(19.489605556202083, -99.14479694505052),
              23:(19.445569636403686, -99.08498554993281),
              24:(19.50563586852945, -99.20001173559454),
              25:(19.377069320063562, -99.18793477375227),
              26:(19.44472323435389, -99.13855468113948),
              27:(19.356570020352297, -99.10121519949078)
    }

def calcular_distancia(nodo1, nodo2):
    x1,y1 = nodos[nodo1]
    x2,y2 = nodos[nodo2]
    distancia = np.sqrt((x2-x1)**2 + (y2-y1)**2)
    return distancia

conec = [(0,1),(0,25),(0,15),(0,7),
         (1,8),(1,2),(1,15),
         (2,9),(2,3),(2,10),
         (3,9),(3,4),(3,10),
         (4,19),(4,5),(4,20),
         (5,19),(5,23),(5,6),
         (6,23),(6,20),
         (7,24),(7,8),
         (8,14),(8,9),
         (9,26),
         (10,15),(10,20),(10,11),(10,21),
         (11,16),(11,27),
         (12,22),(12,17),(12,13),
         (13,22),(13,18),(13,14),
         (14,26),
         (15,16),
         (16,25),
         (17,18),
         (18,23),(18,19),
         (19,26),
         (20,21),
         (21,27),
         (22,24)]

def ACO(inicio, final):
    conexiones = {}
    for (nodo1,nodo2) in conec:
        dist = calcular_distancia(nodo1, nodo2)
        conexiones[(min(nodo1,nodo2),max(nodo1,nodo2))] = dist

    # Parámetros del algoritmo
    rho = 0.9           # Tasa de evaporación
    alpha = 1.0         # Importancia de las feromonas
    beta = 1.0          # Importancia de la heurística
    Q = 1              # Cantidad de feromona depositada
    num_hormigas = 40  
    num_iteraciones = 100
    
    # Feromonas y Heuristica
    feromonas = {arista: 0.01 for arista in conexiones}
    heuristica = {arista: 1.0/conexiones[arista] for arista in conexiones}

    # Matriz de adyacencia para los nodos conectados
    num_nodos = max(max(nodo1, nodo2) for nodo1, nodo2 in conec) + 1
    matriz_caminos = [[False] * num_nodos for _ in range(num_nodos)]
    for nodo1, nodo2 in conec:
        matriz_caminos[nodo1][nodo2] = True
        matriz_caminos[nodo2][nodo1] = True

    mejor_camino_global = None
    mejor_longitud_global = float('inf')

    for iteracion in range(num_iteraciones):
        caminos_todos = []
        longitudes_todos = []
        
        for hormiga in range(num_hormigas):
            nodo_actual = inicio
            camino = [nodo_actual]
            nodos_visitados = {nodo_actual}
            longitud_total = 0
            
            while nodo_actual != final:
                posibles_caminos = [i for i in range(num_nodos) 
                                  if matriz_caminos[nodo_actual][i] and i not in nodos_visitados]
                
                if not posibles_caminos:
                    break
                
                probabilidades = []
                denominador = 0
                for siguiente in posibles_caminos:
                    arista = (min(nodo_actual, siguiente), max(nodo_actual, siguiente))
                    if arista in feromonas:
                        proba = (feromonas[arista]**alpha) * (heuristica[arista]**beta)
                        probabilidades.append(proba)
                        denominador += proba
                    else:
                        probabilidades.append(0)
                
                if denominador == 0:
                    break
                
                probabilidades = [p/denominador for p in probabilidades]
                siguiente = np.random.choice(posibles_caminos, p=probabilidades)
                arista = (min(nodo_actual, siguiente), max(nodo_actual, siguiente))
                
                longitud_total += conexiones[arista]
                nodo_actual = siguiente
                nodos_visitados.add(siguiente)
                camino.append(siguiente)
            
            if nodo_actual == final:
                caminos_todos.append(camino)
                longitudes_todos.append(longitud_total)
        
        if longitudes_todos:
            mejor_iter = min(longitudes_todos)
            mejor_index = longitudes_todos.index(mejor_iter)
            
            if mejor_iter < mejor_longitud_global:
                mejor_longitud_global = mejor_iter
                mejor_camino_global = caminos_todos[mejor_index]
        
        for arista in feromonas:
            feromonas[arista] *= (1 - rho)
        
        if caminos_todos:
            for camino, longitud in zip(caminos_todos, longitudes_todos):
                deposito = Q / longitud
                for i in range(len(camino)-1):
                    arista = (min(camino[i], camino[i+1]), max(camino[i], camino[i+1]))
                    if arista in feromonas:
                        feromonas[arista] += deposito

    return mejor_camino_global, mejor_longitud_global

""" Estaciones"""
estaciones_mostrar = tuple(elec.keys())

""" variables Globales"""
selec_inicio = None
selec_fin = None

global elec_original, nodos_original, conec_original
elec_original = elec.copy()
nodos_original = nodos.copy()
conec_original = conec.copy()

estaciones_inhabilitadas = set()

""" APP"""
app = tk.Tk()
app.geometry("400x700")
app.title("App del metro")

# Colores 
gris_fondo = 'black'
verde_letras = '#01DF01'

app.config(background=gris_fondo)

logo = Image.open("logo.png")
logo = logo.resize((50, 50))
logo_image = ImageTk.PhotoImage(logo)

# Label para el logo
logo_label = tk.Label(image=logo_image, bg='black')
logo_label.pack()

# integrantes = tk.Label(app,
#                     text='Integrantes: Jessica Mariana Monroy Mejia, Aaron Jair Romero Solis y Arián Villalba Tapia',
#                     font=('Arial', 10, 'bold'),
#                     bg='black',
#                     fg='white',
#                     wraplength=300)
# integrantes.pack(pady=10)

instrucciones = tk.Label(app,
                          text='Seleccione el inicio y destino de su ruta',
                          font=('Arial', 10, 'bold'),
                          bg='black',
                          fg='white')
instrucciones.pack()

estilo_boton = {
    'font': ('Arial', 12, 'bold'),  
    'width': 18,                   
    'height': 1,                    
    'cursor': 'hand2',            
    'relief': 'raised',             
    'bd': 3,                        
    'bg': '#FF8C00',               
    'fg': 'white',                  
    'activebackground': '#FF6B00',  
    'activeforeground': 'white'     
}   

boton_mapa = tk.Button(app,
                           text='Mapa',
                           command=mostrar_imagen,
                           **estilo_boton)
boton_mapa.pack()

etiqueta_inicio = tk.Label(app,
                           text="Inicio de su ruta",
                           font=('Arial', 10, 'bold'),
                           bg='black',
                           fg='white')
etiqueta_inicio.pack()

lista_inicio = tk.Listbox(app)
lista_inicio.insert(tk.END, *estaciones_mostrar)
lista_inicio.pack()
lista_inicio.bind("<<ListboxSelect>>", on_select_inicio)

etiqueta_destino = tk.Label(app,
                            text='Destino',
                            font=('Arial', 10, 'bold'),
                            bg='black',
                            fg='white')
etiqueta_destino.pack()

lista_destino = tk.Listbox(app)
lista_destino.pack()
lista_destino.bind("<<ListboxSelect>>", on_select_fin)

boton_calcular = tk.Button(app,
                           text='Calcular',
                           command=calcular_ruta,
                           **estilo_boton)
boton_calcular.pack()



etiqueta_camino = tk.Label(app,
                           text='Ruta:',
                           font=('Arial', 10, 'bold'),
                           bg='black',
                           fg='white',
                           wraplength=350)
etiqueta_camino.pack()

boton_inhabilitado = tk.Button(app,
                               text='Estaciones inhabilitadas',
                               command=inhabilitadas,
                               **estilo_boton)
boton_inhabilitado.pack()

boton_restaurar = tk.Button(app,
                            text='Restaurar estaciones',
                            command=restaurar_estaciones,
                            **estilo_boton)
boton_restaurar.pack()

app.mainloop()