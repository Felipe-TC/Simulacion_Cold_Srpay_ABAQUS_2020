# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-18.54.59 126836
# Run by Magister12 on Tue Dec 22 14:24:32 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
#: Warning: Permission was denied for "abaqus.rpy"; "abaqus.rpy.369" will be used for this session's replay file.

#import random
import math
import numpy as np
#import itertools

from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=396.025024414063, 
    height=167.297790527344)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup






# ----------------------- o ------------------------
# Definicion de funciones




# Generador de patron de Datum Planes 
# tener presente que esta genera datum planes en la seccion Part, la cual tiene un CSYS en el costado de la figura.
# part_name = 'Blank_3D_CS'
def datum_Planes_Patron_Generator(model_name, part_name, number_of_datum_planes, distance_between_planes, highest_y, lowest_y):
    Highest_datum_plane = highest_y - distance_between_planes
    Lower_limit  = highest_y - (number_of_datum_planes + 1) * distance_between_planes
    if Lower_limit + distance_between_planes < lowest_y:
        print 'Error'
        return
    else:
        Positions_y = np.arange(Highest_datum_plane, Lower_limit, - distance_between_planes)
        
        # Generacion de todos los datum planes
        for i in range(number_of_datum_planes):
            p = mdb.models[model_name].parts[part_name]
            p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=Positions_y[i])



# Delete Mesh Interior and Middle
# part_name = 'Blank_3D_CS'
def delete_Mesh_Interior_Middle_Substrate(model_name, part_name):
    p = mdb.models[model_name].parts[part_name]
    c = p.cells
    pickedRegions = c.getSequenceFromMask(mask=('[#da ]', ), )
    p.deleteMesh(regions=pickedRegions)


# Delete Mesh Exterior
def delete_Mesh_Exterior_one_Cell_Substrate(model_name, part_name, x1, y1, z1):
    p = mdb.models[model_name].parts[part_name]
    c = p.cells
    pickedRegions = c.findAt(((x1, y1, z1),))
    p.deleteMesh(regions=pickedRegions)    


# Genera todas las particiones en base a los Datum Planes anteriores.
# first_label_datum_plane = Formato int. Empieza en 143, termina segun la cantidad de planos que se generaron
# last_label_datum_planes = Formato int. Depende de la cantidad de datum planes que hay. Debiera ser = (first_label_datum_plane + number_of_datum_planes - 1)
def partitions_Cell_By_Datum_Planes(model_name, part_name, x_cell, y_cell, z_cell, first_label_datum_plane, last_label_datum_planes):
    for i in range(first_label_datum_plane, last_label_datum_planes + 1):
        p = mdb.models[model_name].parts[part_name]
        c = p.cells
        x = x_cell
        y = y_cell
        z = z_cell
        pickedCells = c.findAt(((x, y, z),))
        d = p.datums
        p.PartitionCellByDatumPlane(datumPlane=d[i], cells=pickedCells)
        
        
# Regenerate Mesh on Blank
def regenerate_Mesh_Interior_Middle_Substrate(model_name, part_name):
    p = mdb.models[model_name].parts[part_name]
    p.generateMesh()
    

# Assign stress field to one Cell
# layer_name        = 'Layer_1' en formato string
# stress_name_layer = 'Stress_Layer_1'
# x_cell, y_cell, z_cell = se ubican según el CSYS de Assembly. Este esta posicionado en la parte de arriba, de forma conveniente definido por mi.
def assign_Stress_Field_to_Cell(model_name, part_name, x_cell, y_cell, z_cell, layer_name, stress_name_layer, s11, s22, s33, s12, s13, s23):
    a = mdb.models[model_name].rootAssembly
    c1 = a.instances[part_name + '-1'].cells
    cells1 = c1.findAt(((x_cell, y_cell , z_cell),))
    region = a.Set(cells=cells1, name=layer_name)
    mdb.models[model_name].Stress(name=stress_name_layer, region=region, 
        distributionType=UNIFORM, sigma11=s11, sigma22=s22, sigma33=s33, 
        sigma12=s12, sigma13=s13, sigma23=s23)




# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------
# -------------------------------------------------




# Seccion Lectura .rpt
# ------------------------------------------------ o -----------------------------------------------------

# --------------------- o ---------------------

# DEFINICION DE FUNCIONES

# Definir funcion que lee los rpt de abaqus
# Retorna un arreglo tipo numpy, en donde cada fila es una capa y cada columna es el
# S11 del elemento
# --
# rpt_name : String con el nombre del archivo .rpt
def lector_rpt_Abaqus(rpt_name, stress_requested):
    with open(rpt_name) as f:
        lis = [line.split() for line in f] # create a list of lists. Every list inside lis is a row
        L = []          # Inicializa una lista vacia que guardara los valores de cada capa
        for x in lis:   # Recorre las listas adentro de lis
            if x != []:
                if x[0] != 'X':
                    if not stress_requested in x[0]:
                        L.append(x)            
        Jaja = np.array(L)
        Jeje = Jaja.astype(np.float)
        return Jeje
    
    
# Definir funcion que genera un np.array con los valores de la linea
def generador_Array(list_string):
    list_string2 = list(map(float, list_string[0].split()))
    return np.array(list_string2)


# S11: np.array del esfuerzo S11 de cada elemento. Esta ordenado en filas(capas - frames)
#       y cada columna es el S11 de cada elemento
# frame_requested: El frame que se está pidiendo. Parte desde 0 y llega a 20 en el .rpt
def generador_Array_por_Frame(S11, frame_requested, number_of_frames, number_of_layers):
    L = []
    i = frame_requested
    for lay in range(number_of_layers):
        L.append(S11[i])
        i = i + number_of_frames
    Jaja = np.array(L)
    Jeje = Jaja.astype(np.float)
    return Jeje
        
        
        

# ---------------------------- o ---------------------------
# Obtencion datos averages para cada capa a partir de rpts

step_pedido = 'Shot'
simulation          = 1

number_of_frames = 41
number_of_layers = 74
frame_requested = 40

# S11 -------- o ----------
stress_requested    = 'S11'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S11         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S11_frame_with_time = generador_Array_por_Frame(S11, frame_requested, number_of_frames, number_of_layers)

S11_frame   = S11_frame_with_time[:, 1:]
S11_only_times = S11_frame_with_time[:, 0]
Averages_S11 = np.mean(S11_frame, axis=1)


# S22 -------- o ----------
stress_requested    = 'S22'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S22         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S22_frame_with_time = generador_Array_por_Frame(S22, frame_requested, number_of_frames, number_of_layers)

S22_frame   = S22_frame_with_time[:, 1:]
S22_only_times = S22_frame_with_time[:, 0]
Averages_S22 = np.mean(S22_frame, axis=1)


# S33 -------- o ----------
stress_requested    = 'S33'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S33         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S33_frame_with_time = generador_Array_por_Frame(S33, frame_requested, number_of_frames, number_of_layers)

S33_frame   = S33_frame_with_time[:, 1:]
S33_only_times = S33_frame_with_time[:, 0]
Averages_S33 = np.mean(S33_frame, axis=1)


# S12 -------- o ----------
stress_requested    = 'S12'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S12         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S12_frame_with_time = generador_Array_por_Frame(S12, frame_requested, number_of_frames, number_of_layers)

S12_frame   = S12_frame_with_time[:, 1:]
S12_only_times = S12_frame_with_time[:, 0]
Averages_S12 = np.mean(S12_frame, axis=1)


# S13 -------- o ----------
stress_requested    = 'S13'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S13         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S13_frame_with_time = generador_Array_por_Frame(S13, frame_requested, number_of_frames, number_of_layers)

S13_frame   = S13_frame_with_time[:, 1:]
S13_only_times = S13_frame_with_time[:, 0]
Averages_S13 = np.mean(S13_frame, axis=1)


# S23 -------- o ----------
stress_requested    = 'S23'

rpt_name    = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\scripts\Input_Residual_Stress\CS_Reporte_' + stress_requested + '_elementos_capas_' + step_pedido + '_frame0-1_Sim' + str(simulation) + '.rpt'
S23         = lector_rpt_Abaqus(rpt_name, stress_requested)   # Genera un arreglo de 'capas(filas) X elementos(columnas)'
S23_frame_with_time = generador_Array_por_Frame(S23, frame_requested, number_of_frames, number_of_layers)

S23_frame   = S23_frame_with_time[:, 1:]
S23_only_times = S23_frame_with_time[:, 0]
Averages_S23 = np.mean(S23_frame, axis=1)











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


model_name = 'My_Investigation_Input_Stress_Substrate'




executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.

session.viewports['Viewport: 1'].setValues(displayedObject=None)
openMdb(
    pathName='D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021/FOR_SCRIPTING_Input_Residual_Stress/FOR_SCRIPTING_My_Investigation_Input_Residual_Stress_on_Substrate_only.cae')
#: The model database "D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\TEST_Input_Stress\Sim1\TEST_Input_Stress.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models[model_name].parts['Blank_3D_CS']
session.viewports['Viewport: 1'].setValues(displayedObject=p)


part_name               = 'Blank_3D_CS'
number_of_datum_planes  = number_of_layers / 2
distance_between_planes = 0.0035294117647058
highest_y               = 0.15
lowest_y                = -0.15


# Creacion de Datum Planes
datum_Planes_Patron_Generator(model_name, part_name, number_of_datum_planes, distance_between_planes, highest_y, lowest_y)

# Delete Mesh
delete_Mesh_Interior_Middle_Substrate(model_name, part_name)

# Partition Cell with Datum Planes
x_cell = 0.00
y_cell = lowest_y + 0.01
z_cell = 0.15
first_label_datum_plane = 143
last_label_datum_planes = first_label_datum_plane + number_of_datum_planes - 1
partitions_Cell_By_Datum_Planes(model_name, part_name, x_cell, y_cell, z_cell, first_label_datum_plane, last_label_datum_planes)

# Regenerate Mesh
regenerate_Mesh_Interior_Middle_Substrate(model_name, part_name)

# Assign Stress Field to Cell
jj = 0
for i in range(number_of_datum_planes):
    x_cell =    0.0
    y_cell = -  ((i + 1) * distance_between_planes - distance_between_planes / 2)
    z_cell =    0.0
    layer_name = 'Layer_' + str(i + 1)
    stress_name_layer = 'Stress_Layer_' + str(i + 1)
    s11 = (Averages_S11[jj] + Averages_S11[jj+1]) / 2
    s22 = (Averages_S22[jj] + Averages_S22[jj+1]) / 2
    s33 = (Averages_S33[jj] + Averages_S33[jj+1]) / 2
    s12 = (Averages_S12[jj] + Averages_S12[jj+1]) / 2
    s13 = (Averages_S13[jj] + Averages_S13[jj+1]) / 2
    s23 = (Averages_S23[jj] + Averages_S23[jj+1]) / 2
    jj = jj + 2
    assign_Stress_Field_to_Cell(model_name, part_name, x_cell, y_cell, z_cell, layer_name, stress_name_layer, s11, s22, s33, s12, s13, s23)