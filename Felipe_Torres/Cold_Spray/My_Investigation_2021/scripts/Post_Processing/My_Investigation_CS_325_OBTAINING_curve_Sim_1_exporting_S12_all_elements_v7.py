# Este codigo debe ser ejecutado con el modelo cerrado. El codigo abre el modelo y el odb

# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-18.54.59 126836
# Run by Magister12 on Thu Aug 06 15:06:36 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=228.392501831055, 
    height=109.084449768066)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
import numpy as np








# Crear xy Data de cada elemento de una capa
# odb_name se saca de abajo
# first_element = 966025
# last_element = 968065
# size_of_square = 31 x 31 elementos
# avance en columnas = 67 en 67 elementos ---> 966025 + 67 = 966092
# stress_type   : String del tipo se esfuerzo que se pide. En este caso 'S11'
def creating_Stress_xy_data_one_layer(odb_name, stress_type, first_element, last_element, size_of_square, avance_en_columnas, step_pedido, frame_pedido):
    # session.viewports['Viewport: 1'].setValues(displayedObject=o3)
    odbName=session.viewports[session.currentViewportName].odbDisplay.name
    session.odbData[odbName].setValues(activeFrames=((step_pedido, (frame_pedido, )), ))
    # odb = session.odbs['D:/Pipe/Tesis/ABAQUS_Various/Outputs_Abaqus/Gariepy_2011_15_Part_Sim1.odb']
    # session.xyDataListFromField(odb=odb, outputPosition=INTEGRATION_POINT, 
        # variable=(('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), )), ), 
        # elementLabels=(('BLANK_3D_CS-1', ('966025:966055', )), ))
    odb = session.odbs[odb_name]
    zz = size_of_square # Filas
    xx = size_of_square # Columnas
    XX_array = np.zeros((zz, xx), dtype=int)
    XX_extremos = []      # np.zeros((xx,), dtype=int)
    
    first_element_column = int(first_element) # Inicializa la variable en 966025
    for k in range(xx): # Columnas
        XX_array[:, k] = np.arange(int(first_element_column), int(first_element_column + zz), dtype=int)
        if not isinstance(XX_array[0, k], (int, long)):
            print 'Errorcito elmano mio'
            break
        else:
            #print str(int(XX_array[0, k])) + ':' + str(int(XX_array[-1, k]))
            #print XX_extremos[k]
            XX_extremos.append(str(int(XX_array[0, k])) + ':' + str(int(XX_array[-1, k])))
            first_element_column = int(first_element_column + avance_en_columnas)
    
    XX_tupla = tuple(XX_extremos)
    session.xyDataListFromField(odb=odb, outputPosition=INTEGRATION_POINT, 
    variable=(('S', INTEGRATION_POINT, ((COMPONENT, stress_type), )), ), 
    elementLabels=(('BLANK_3D_CS-1', XX_tupla), ))
    return XX_array
    
    
    
    
    
    
# Calculo del promedio avg() de los datos XY    
# elements_array = numpy array, igual al XX_array que contiene los labels de los elementos de una sola capa, en formato NO string
# capa  : Capa (numero) a la que se le esta calculando el promedio. int()
# stress_type   : String del tipo se esfuerzo que se pide. En este caso 'S11'
def creating_Stress_Average_one_layer(stress_type, elements_array, size_of_square, capa):
    zz = size_of_square # Filas
    xx = size_of_square # Columnas
    Objects_array = []  # np.zeros(zz * xx) # Inicializa el array con los objetos que les tomara su Average (promedio) 1D array
    
    l = 0 # Index para moverse en el Objects_array
    for i in range(zz): # Filas
        for k in range(xx): # Columnas
            #print str(elements_array[i, k])
            Objects_array.append(session.xyDataObjects['S:' + stress_type + ' PI: BLANK_3D_CS-1 E: ' + str(elements_array[i, k]) + ' IP: 1'])
            l = l + 1
    
    Objects_tupla = tuple(Objects_array)
    Average_avg = avg(Objects_tupla)
    Average_avg.setValues(
        sourceDescription= stress_type + ' Promedio capa ' + str(capa))
    tmpName = Average_avg.name
    session.xyDataObjects.changeKey(tmpName, stress_type + '_Promedio_Capa_' + str(capa))
    
    
    
    
   







# Generar reporte en base a los promedios de cada capa
# nro_capas : Cantidad de capas (layers)
# simulacion : numero de la simulacion, por ejemplo Sim 1
# stress_type   : String del tipo se esfuerzo que se pide. En este caso 'S11'
def generate_Report(stress_type, nro_capas, simulacion, append_mode):
    Promedios_array = [] # np.zeros(nro_capas)
    
    # Recorrer cada capa y guardar su promedio
    for h in range(nro_capas):
        Promedios_array.append(session.xyDataObjects[stress_type + '_Promedio_Capa_' + str(h + 1)])

    Promedios_tupla = tuple(Promedios_array)
    nombre_archivo = 'CS_Reporte_' + stress_type + '_Promedios_Capas_Sim' + str(simulacion) + '.rpt'
    session.xyReportOptions.setValues(totals=OFF, minMax=OFF)
    session.writeXYReport(fileName=nombre_archivo, appendMode=append_mode, xyData=Promedios_tupla)
    








# Generar reporte de los elementos de solo una capa
# elements_array = numpy array, igual al XX_array que contiene los labels de los elementos de una sola capa, en formato NO string
# simulacion : numero de la simulacion, por ejemplo Sim 1
# stress_type   : String del tipo se esfuerzo que se pide. En este caso 'S11'
# size_of_square = 31 x 31 elementos
# capa  : Capa (numero) a la que se le esta calculando el promedio. int()
def generate_Report_each_element_layer(stress_type, elements_array, size_of_square, capa, simulacion, step_pedido, frame_pedido, append_mode = ON):
    zz = size_of_square # Filas
    xx = size_of_square # Columnas    
    Stress_elements_list = [] # np.zeros(nro_capas)
    
    # Recorrer cada capa y guardar su promedio
    for i in range(zz): # Filas
        for k in range(xx): # Columnas
            
            if ':' in frame_pedido:
                pupi = frame_pedido.find(':')
                frame_pedido_mientras = frame_pedido[0:pupi] + frame_pedido[pupi + 1 :]
                new_name_XY_data_element = stress_type + '_fr' + str(frame_pedido_mientras) + '_' + str(elements_array[i, k]) + '_' + str(capa) 
            else:
                new_name_XY_data_element = stress_type + '_fr' + str(frame_pedido) + '_' + str(elements_array[i, k]) + '_' + str(capa) 
            
            temp_Stress = session.xyDataObjects['S:' + stress_type + ' PI: BLANK_3D_CS-1 E: ' + str(elements_array[i, k]) + ' IP: 1']
            tmpName = temp_Stress.name
            session.xyDataObjects.changeKey(tmpName, new_name_XY_data_element)
            Stress_elements_list.append(session.xyDataObjects[new_name_XY_data_element])

    Stress_elements_tupla = tuple(Stress_elements_list)
    
    if ':' in frame_pedido:
        pipu = frame_pedido.find(':')
        framito = frame_pedido[0:pipu] + frame_pedido[pipu + 1 :]
        nombre_archivo = 'CS_Reporte_' + stress_type + '_elementos_capas_' + step_pedido + '_frame' + str(framito) + '_Sim' + str(simulacion) + '.rpt'
    else:
        nombre_archivo = 'CS_Reporte_' + stress_type + '_elementos_capas_' + step_pedido + '_frame' + str(frame_pedido) + '_Sim' + str(simulacion) + '.rpt'

    session.xyReportOptions.setValues(totals=OFF, minMax=OFF)
    session.writeXYReport(fileName=nombre_archivo, appendMode=append_mode, xyData=Stress_elements_tupla)

    

    
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------

# BEGINNING OF DOCUMENT
# ------------------------------------------------ o -----------------------------------------------------
    

# Model Data Base and ODB names to open them
mdb_name = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\My_Investigation_2021_325_Particles_Randomized\Sim1\Sim1_My_Investigation_325.cae'
odb_name = 'D:\Pipe\Tesis\ABAQUS_Various\Outputs_Abaqus\Sim1_My_Inv_325_Particles_Randomized.odb'


executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
openMdb(
    pathName=mdb_name)
#: The model database "D:\Pipe\Tesis\ABAQUS_Various\CAEs\Shot_Peening_3D\Shot_Peening_3D_15_part_TODO_random_Definitivo\Sim1\Gariepy_2011_Sim1.cae" has been opened.
# session.viewports['Viewport: 1'].setValues(displayedObject=None)
# p = mdb.models['Shot_3D_Gariepy_15_Particles_Sim1'].parts['Blank']
# session.viewports['Viewport: 1'].setValues(displayedObject=p)
# a = mdb.models['Shot_3D_Gariepy_15_Particles_Sim1'].rootAssembly
# session.viewports['Viewport: 1'].setValues(displayedObject=a)
# session.viewports['Viewport: 1'].assemblyDisplay.setValues(
    # optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
o3 = session.openOdb(
    name=odb_name)
#: Model: D:/Pipe/Tesis/ABAQUS_Various/Outputs_Abaqus/Gariepy_2011_15_Part_Sim1.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     16
#: Number of Meshes:             16
#: Number of Element Sets:       35
#: Number of Node Sets:          36
#: Number of Steps:              1
session.viewports['Viewport: 1'].setValues(displayedObject=o3)


step_pedido = 'Shot'
# Verificacion: Se pediran todos los frames?
Todos_Frames = True
if Todos_Frames == True:
    frame_pedido = '0:-1'   # Si se estan pidiendo todos los frames, poner el frame final
else:
    frame_pedido = 1        # Si se pide solo 1 frame, poner el frame pedido.



# Parametros Globales del Field Output Request --------------------------- o ----------------------------------
stress_type = 'S12'     # Estress en x = S11,  o z = S33
size_of_square = 31     # Elementos por lado
avance_en_columnas = 65 # Este es un avance real, sacado de la diferencia como tal. Me paro en un elemento, sumo 67 y da la siguiente columna
first_element = 1546963 # Aqui se fija el primer elemento de todos. Se ira actualizando en el for.
simulacion = 1
nro_capas = 74          # En el cuaderno. 0.6 / 0.015
avance_en_capas = 4160  # Avance en las capas hacia abajo. Tambien es avance real






# Ejecucion del Post Processing --------------------------------------- o --------------------------------------

#  Creacion de los promedios de cada capa
for i in range(nro_capas):
    capa = i+1
    last_element = int(first_element + ((size_of_square - 1) * (size_of_square) + (avance_en_columnas - (size_of_square - 1)) * (size_of_square)))  # 30*31 avance 30 en filas, 31 veces  ---  37*30 avance a la sgte columna luego de recorrer la fila (37), 30 veces
    elements_array = creating_Stress_xy_data_one_layer(odb_name, stress_type, first_element, last_element, size_of_square, avance_en_columnas, step_pedido, frame_pedido)
    if not isinstance(elements_array[0, 0], (int, long)):
        print 'Errorcito elmano mio en el for abajo'
        break
    else:
        # ## NO OCUPADA ## creating_Stress_Average_one_layer(stress_type, elements_array, size_of_square, capa)
        # Creacion de reporte del Stress S11 de los elementos de la presente capa
        generate_Report_each_element_layer(stress_type, elements_array, size_of_square, capa, simulacion, step_pedido, frame_pedido, append_mode = ON)
        first_element = int(first_element + avance_en_capas)
 
append_mode = OFF
# ## NO OCUPADA ## generate_Report(stress_type, nro_capas, simulacion, append_mode)

