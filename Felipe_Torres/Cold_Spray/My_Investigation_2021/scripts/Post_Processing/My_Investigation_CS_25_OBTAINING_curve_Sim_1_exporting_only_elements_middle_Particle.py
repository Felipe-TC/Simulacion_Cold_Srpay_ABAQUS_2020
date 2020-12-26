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








# Crear xy Data de cada elemento de una capa de una sola particula
# odb_name se saca de abajo
# stress_type   : String del tipo de esfuerzo que se pide. En este caso 'S11'
# elements_array_one_layer  : numpy array, que contiene los elementos de solo una capa, de una particula.
# particle_name     : nombre de la particula en formato string
def creating_Stress_xy_data_one_layer_one_particle(odb_name, stress_type, elements_array_one_layer, particle_name, step_pedido, frame_pedido):
    odbName=session.viewports[session.currentViewportName].odbDisplay.name
    session.odbData[odbName].setValues(activeFrames=((step_pedido, (frame_pedido, )), ))
    # odb = session.odbs['D:/Pipe/Tesis/ABAQUS_Various/Outputs_Abaqus/Gariepy_2011_15_Part_Sim1.odb']
    # session.xyDataListFromField(odb=odb, outputPosition=INTEGRATION_POINT, 
        # variable=(('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), )), ), 
        # elementLabels=(('BLANK_3D_CS-1', ('966025:966055', )), ))
    odb = session.odbs[odb_name]
    Instance_Name = particle_name + '-1'
    
    Array_in_tuple = tuple(elements_array_one_layer)
    session.xyDataListFromField(odb=odb, outputPosition=INTEGRATION_POINT, 
    variable=(('S', INTEGRATION_POINT, ((COMPONENT, stress_type), )), ), 
    elementLabels=((Instance_Name, Array_in_tuple), ))
    
    
    
    
# Generar reporte de los elementos de solo una capa
# elements_array_one_layer = numpy array, igual al XX_array que contiene los labels de los elementos de una sola capa, en formato NO string
# simulacion : numero de la simulacion, por ejemplo Sim 1
# stress_type   : String del tipo se esfuerzo que se pide. En este caso 'S11'
# particles_array : np.array que contiene el nro de las particulas pedidas. Formato int.
# capa  : Capa (numero) a la que se le esta calculando el promedio. int(). En total son 10 capas
# step_pedido : formato string del step pedido (shot or disipation)
def generate_Report_each_element_layer(stress_type, elements_array_one_layer, particles_array, capa, simulacion, step_pedido, frame_pedido, append_mode = ON):
    Stress_elements_list = [] # np.zeros(nro_capas)
    
    # Recorrer las particulas pedidas
    for kk in particles_array:
        for elementito in elements_array_one_layer:
            Instance_Name = 'PARTICLE_3D_CS-' + str(kk) + '-1'
            if ':' in frame_pedido:
                pupi = frame_pedido.find(':')
                frame_pedido_mientras = frame_pedido[0:pupi] + frame_pedido[pupi + 1 :]
                new_name_XY_data_element = Instance_Name + '_' + stress_type + '_' + step_pedido + '_fr' + str(frame_pedido_mientras) + '_' + str(elementito) + '_' + str(capa) 
            else:
                new_name_XY_data_element = Instance_Name + '_' + stress_type + '_' + step_pedido + '_fr' + str(frame_pedido) + '_' + str(elementito) + '_' + str(capa) 
            
            temp_Stress = session.xyDataObjects['S:' + stress_type + ' PI: ' + Instance_Name + ' E: ' + str(elementito) + ' IP: 1']
            tmpName = temp_Stress.name
            session.xyDataObjects.changeKey(tmpName, new_name_XY_data_element)
            Stress_elements_list.append(session.xyDataObjects[new_name_XY_data_element])        

    Stress_elements_tupla = tuple(Stress_elements_list)
    
    if ':' in frame_pedido:
        pipu = frame_pedido.find(':')
        framito = frame_pedido[0:pipu] + frame_pedido[pipu + 1 :]
        nombre_archivo = 'CS_Reporte_Particles_' + str(particles_array[0]) + '_' + str(particles_array[-1]) + '_' + stress_type + '_elementos_capas_' + step_pedido + '_frame' + str(framito) + '_Sim' + str(simulacion) + '.rpt'
    else:
        nombre_archivo = 'CS_Reporte_Particles_' + str(particles_array[0]) + '_' + str(particles_array[-1]) + '_' + stress_type + '_elementos_capas_' + step_pedido + '_frame' + str(frame_pedido) + '_Sim' + str(simulacion) + '.rpt'

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
mdb_name = 'D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021\DEPOSITION_25_Particles_DisipationStep_MoreDamping\Sim1\Sim1_My_Investigation_Deposition_Damping_25_particles.cae'
odb_name = 'D:\Pipe\Tesis\ABAQUS_Various\Outputs_Abaqus\My_Invstigtn_25_Deposition_Dmpng_Disip.odb'


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


step_pedido = 'Disipation'
# Verificacion: Se pediran todos los frames?
Todos_Frames = True
if Todos_Frames == True:
    frame_pedido = '0:-1'   # Si se estan pidiendo todos los frames, poner el frame final
else:
    frame_pedido = 1        # Si se pide solo 1 frame, poner el frame pedido.



# Parametros Globales del Field Output Request --------------------------- o ----------------------------------
stress_type = 'S33'     # Estress en x = S11,  o z = S33

# Array de los elementos por cada capa
elements_array = np.array([[419, 420, 423, 424, 531, 532, 535, 536, 595, 596, 599, 600, 865, 866, 869, 870],
[337, 341, 353, 357, 465, 469, 481, 485, 659, 660, 663, 664, 815, 816, 831, 832],
[338, 342, 354, 358, 466, 470, 482, 486, 643, 644, 647, 648, 811, 812, 827, 828],
[339, 343, 355, 359, 467, 471, 483, 487, 627, 628, 631, 632, 807, 808, 823, 824],
[340, 344, 356, 360, 468, 472, 484, 488, 611, 612, 615, 616, 803, 804, 819, 820],
[20, 24, 36, 40, 116, 120, 132, 136, 244, 248, 260, 264, 691, 692, 707, 708],
[19, 23, 35, 39, 115, 119, 131, 135, 243, 247, 259, 263, 695, 696, 711, 712],
[18, 22, 34, 38, 114, 118, 130, 134, 242, 246, 258, 262, 699, 700, 715, 716],
[17, 21, 33, 37, 113, 117, 129, 133, 241, 245, 257, 261, 703, 704, 719, 720],
[83, 84, 87, 88, 195, 196, 199, 200, 307, 308, 311, 312, 753, 754, 757, 758]])

# Array particles
particles_array = np.array([7, 8, 12, 13, 14, 18, 19])

simulacion = 1
nro_capas = 10    






# Ejecucion del Post Processing --------------------------------------- o --------------------------------------
# Creacion x - y data
for ii in range(nro_capas):
    capa = ii + 1
    elements_array_one_layer = elements_array[ii]
    for particulita in particles_array:
        particle_name = 'PARTICLE_3D_CS-' + str(particulita)
        creating_Stress_xy_data_one_layer_one_particle(odb_name, stress_type, elements_array_one_layer, particle_name, step_pedido, frame_pedido)
    # Generacion del reporte
    generate_Report_each_element_layer(stress_type, elements_array_one_layer, particles_array, capa, simulacion, step_pedido, frame_pedido, append_mode = ON)

    
append_mode = OFF
# ## NO OCUPADA ## generate_Report(stress_type, nro_capas, simulacion, append_mode)

