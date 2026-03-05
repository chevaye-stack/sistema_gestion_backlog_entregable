#SISTEMA_GESTION_BACKLOG_FINAL.py
#Trabajo Final - PIAD-216 Algoritmia para el Desarrollo de Programas

import json
import os
import csv
from datetime import datetime #sacamos datetime de su libreria

ARCHIVO = "" #aca se guarda el nombre del archivo que elija el usuario

"""
Funcionalidades:
-Crear, ver, actualizar y eliminar tareas
-Cada tarea tiene un id unico
-Validacion de fechas con datetime
-Manejo de errores con try except
-Menu interactivo
-El usuario puede elegir el nombre del archivo json
-Se puede cambiar de archivo en el menu
-Exportar tareas a CSV y TXT
"""

#funcion para cargar tareas del json
def cargar_tareas():
    try:
        if os.path.exists(ARCHIVO):
            #revisamos que no este vacio el archivo
            if os.path.getsize(ARCHIVO) == 0:
                return []
            with open(ARCHIVO,"r") as archivo:
                return json.load(archivo)
    except json.JSONDecodeError:
        print(f"El archivo {ARCHIVO} esta dañado, se empieza de cero")
    except Exception as e:
        print(f"No se pudo cargar el archivo: {e}")
    return []

#funcion para guardar tareas en el json
def guardar_tarea(tareas):
    try:
        with open(ARCHIVO, "w") as archivo:
            json.dump(tareas, archivo, indent=4) #indent para que se vea ordenado el json
        return True
    except IOError as e:
        print(f"no se pudo guardar: {e}")
        return False

#validar que la prioridad sea correcta
def validar_prioridad(prioridad):
    prioridades_validas = ["Alta","Media","Baja"]
    if prioridad.capitalize() in prioridades_validas:
        return prioridad.capitalize()
    else:
        print("Prioridad invalida. Usa Alta, Media o Baja")
        return None

#crear id automatico
def generar_id(tareas):
    if not tareas:
        return 1
    return max(t["id"] for t in tareas) + 1 #agarra el id mas grande y le suma 1

#validar que la fecha este bien escrita
def validar_fecha(fecha):
    try:
        fecha_agregada = datetime.strptime(fecha, "%Y-%m-%d").date() #pasamos el string a formato fecha
        #que no pongan fechas viejas
        if fecha_agregada < datetime.now().date():
            print("No puedes poner una fecha que ya paso")
            return None
        return fecha_agregada.strftime("%Y-%m-%d") #lo devolvemos como string
    except ValueError:
        print("Formato invalido. Escribe asi: YYYY-MM-DD")
        return None

#funcion para crear tarea nueva
def crear_tarea(tareas):
    descripcion = input("Descripcion: ")
    responsable = input("Responsable: ")

    #pedimos fecha hasta que este bien
    while True:
        fecha = input("Fecha limite(YYYY-MM-DD): ")
        fecha_validada = validar_fecha(fecha)
        if fecha_validada:
            break
    #pedimos prioridad hasta que este bien
    while True:
        prioridad = input("Prioridad(Alta/Media/Baja): ")
        prioridad_validada = validar_prioridad(prioridad)
        if prioridad_validada:
            break

    tarea = {
        "id":generar_id(tareas),
        "descripcion": descripcion,
        "fecha_limite":fecha_validada,
        "responsable": responsable,
        "prioridad": prioridad_validada,
        "estado":"Pendiente"
        }

    tareas.append(tarea)
    if guardar_tarea(tareas):
        print("Tarea creada!")

#funcion para mostrar las tareas
def visualizar_tareas(tareas):
    if not tareas:
        print("No hay tareas todavia")
        return
    
    fecha_actual = datetime.now().date()

    for tarea in tareas:
        fecha_tarea = datetime.strptime(tarea["fecha_limite"], "%Y-%m-%d").date()
        dias_restantes = (fecha_tarea - fecha_actual).days

        #esto es para mostrar si ya vencio o esta por vencer
        estado_auto = ""
        if dias_restantes < 0:
            estado_auto = " [VENCIDA]"
        elif dias_restantes <= 3:
            estado_auto = " [por vencer]"
        
        print("-------------------------------")
        print(f"ID: {tarea['id']}")
        print(f"Descripcion: {tarea['descripcion']}")
        print(f"Fecha Limite: {tarea['fecha_limite']} ({dias_restantes} dias){estado_auto}")
        print(f"Responsable: {tarea['responsable']}")
        print(f"Prioridad: {tarea['prioridad']}")
        print(f"Estado: {tarea['estado']}")
    print("-------------------------------")

#funcion para actualizar una tarea
def actualizar_tarea(tareas):
    #manejo de error por si ponen letras en vez de numero
    try:
        id_tarea = int(input("Ingresa el ID de la tarea: "))
    except ValueError:
        print("Eso no es un numero valido")
        return
    
    #buscamos la tarea
    for tarea in tareas:
        if tarea["id"] == id_tarea:
            tarea["descripcion"] = input("Nueva descripcion: ")
            tarea["responsable"] = input("Nuevo Responsable: ")
            #validamos la nueva fecha
            while True:
                nueva_fecha = input("Nueva fecha limite(YYYY-MM-DD): ")
                fecha_validada = validar_fecha(nueva_fecha)
                if fecha_validada:
                    tarea["fecha_limite"] = fecha_validada
                    break
            #validamos la nueva prioridad
            while True:
                nueva_prioridad = input("Nueva prioridad(Alta/Media/Baja): ")
                prioridad_validada = validar_prioridad(nueva_prioridad)
                if prioridad_validada:
                    tarea["prioridad"] = prioridad_validada
                    break
            tarea["estado"] = input("Estado(Pendiente/Completo): ")

            guardar_tarea(tareas)
            print("Tarea actualizada")
            return
    print("No se encontro esa tarea")

#funcion para eliminar tarea
def eliminar_tarea(tareas):
    try:
        id_tarea = int(input("Ingresa el ID a eliminar: "))
    except ValueError:
        print("Eso no es un numero valido")
        return

    for tarea in tareas:
        if tarea["id"] == id_tarea:
            tareas.remove(tarea)
            guardar_tarea(tareas)
            print("Tarea eliminada")
            return
    print("No se encontro esa tarea")

#funcion para exportar a CSV
#basicamente agarra las tareas y las pone en una tabla separada por comas
def exportar_csv(tareas):
    if not tareas:
        print("No hay tareas para exportar")
        return
    
    #le pedimos al usuario como quiere que se llame el csv
    nombre = input("Nombre para el archivo CSV (sin extension): ")
    if nombre.strip() == "":
        nombre = "tareas_exportadas"
    nombre_archivo = nombre.strip() + ".csv"
    
    try:
        with open(nombre_archivo, "w", newline="") as archivo:
            #estas son las columnas que va a tener el csv
            columnas = ["id","descripcion","fecha_limite","responsable","prioridad","estado"]
            escritor = csv.DictWriter(archivo, fieldnames=columnas)
            escritor.writeheader() #esto escribe la fila de los titulos
            for tarea in tareas:
                escritor.writerow(tarea) #y esto escribe cada tarea como una fila
        print(f"Exportado a '{nombre_archivo}'!")
    except IOError as e:
        print(f"No se pudo exportar: {e}")

#funcion para exportar a TXT
#esto lo hace mas legible, como un reporte que puedes imprimir
def exportar_txt(tareas):
    if not tareas:
        print("No hay tareas para exportar")
        return
    
    nombre = input("Nombre para el archivo TXT (sin extension): ")
    if nombre.strip() == "":
        nombre = "tareas_exportadas"
    nombre_archivo = nombre.strip() + ".txt"
    
    try:
        with open(nombre_archivo, "w") as archivo:
            archivo.write("========================================\n")
            archivo.write("       REPORTE DE TAREAS\n")
            archivo.write(f"       Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            archivo.write("========================================\n\n")
            
            for tarea in tareas:
                archivo.write(f"ID:           {tarea['id']}\n")
                archivo.write(f"Descripcion:  {tarea['descripcion']}\n")
                archivo.write(f"Fecha Limite: {tarea['fecha_limite']}\n")
                archivo.write(f"Responsable:  {tarea['responsable']}\n")
                archivo.write(f"Prioridad:    {tarea['prioridad']}\n")
                archivo.write(f"Estado:       {tarea['estado']}\n")
                archivo.write("----------------------------------------\n")
            
            archivo.write(f"\nTotal de tareas: {len(tareas)}\n")
        print(f"Exportado a '{nombre_archivo}'!")
    except IOError as e:
        print(f"No se pudo exportar: {e}")

#menu principal
def menu():
    global ARCHIVO
    
    #aca le pedimos al usuario que ponga el nombre de su archivo
    print("=== Gestor de Tareas ===")
    nombre = input("Como quieres que se llame tu archivo? (ej: trabajo, universidad, casa): ")
    if nombre.strip() == "":
        nombre = "mis_tareas"
    #le agregamos el .json al final
    ARCHIVO = nombre.strip() + ".json"
    
    tareas = cargar_tareas()
    print(f"Usando: '{ARCHIVO}' - {len(tareas)} tareas cargadas")

    while True:
        print("\n----- Gestor de Tareas -----")
        print("1. Crear tarea")
        print("2. Mostrar tareas")
        print("3. Actualizar tarea")
        print("4. Eliminar tarea")
        print("5. Cambiar de archivo")
        print("6. Exportar a CSV")
        print("7. Exportar a TXT")
        print("8. Salir")

        opcion = input("Elige: ")

        if opcion == "1":
            crear_tarea(tareas)
        elif opcion == "2":
            visualizar_tareas(tareas)
        elif opcion == "3":
            actualizar_tarea(tareas)
        elif opcion == "4":
            eliminar_tarea(tareas)
        elif opcion == "5":
            #proceso extra: poder cambiar de archivo sin cerrar el programa
            nuevo = input("Nombre del nuevo archivo: ")
            if nuevo.strip() != "":
                ARCHIVO = nuevo.strip() + ".json"
                tareas = cargar_tareas()
                print(f"Ahora usando: '{ARCHIVO}' - {len(tareas)} tareas cargadas")
            else:
                print("Escribe un nombre")
        elif opcion == "6":
            exportar_csv(tareas)
        elif opcion == "7":
            exportar_txt(tareas)
        elif opcion == "8":
            print("Chau!")
            break
        else:
            print("Opcion invalida")


if __name__ == "__main__":
    menu()

#Explicacion tecnica de las mejoras:
#
#1. Guardado con nombre personalizado
#   Agregue que al inicio el programa te pregunte como quieres llamar tu archivo
#   y le pone .json automaticamente. Tambien con la opcion 5 podes cambiar de archivo.
#   Esto mejora el software porque asi podes tener archivos separados para cada cosa,
#   por ejemplo trabajo.json y universidad.json sin que se mezclen las tareas.
#
#2. Manejo de errores
#   Puse try-except en cargar_tareas por si el json esta roto o vacio,
#   en guardar_tarea por si no se puede escribir el archivo,
#   y en actualizar y eliminar por si el usuario pone letras en vez de un numero de ID.
#   Esto mejora el software porque antes si ponias algo mal el programa se cerraba
#   y ahora te avisa del error y sigue funcionando normal.
#
#3. Logica de las funciones
#   Cada funcion hace una cosa sola. validar_fecha solo valida la fecha,
#   crear_tarea solo crea, etc. Asi es mas facil encontrar errores
#   y si quiero cambiar algo no tengo que tocar todo el codigo.
#
#4. Exportar a CSV (opcion 6)
#   Use la libreria csv que ya viene con python. Lo que hace es agarrar las tareas
#   y ponerlas en formato tabla separada por comas. El usuario elige el nombre del archivo.
#   Esto mejora el software porque el CSV se puede abrir en Excel o Google Sheets
#   y asi el usuario puede ver sus tareas en una tabla, filtrarlas, hacer graficos, etc.
#   Es util para cuando quieres compartir las tareas con alguien que no tiene python.
#
#5. Exportar a TXT (opcion 7)
#   Esto genera un archivo de texto plano con las tareas ordenadas como un reporte.
#   Tambien le pone la fecha de cuando se exporto y el total de tareas al final.
#   Esto mejora el software porque el TXT se puede abrir en cualquier computadora
#   sin necesidad de ningun programa especial. Sirve para imprimir o mandar por correo
#   como un resumen rapido de las tareas pendientes.
