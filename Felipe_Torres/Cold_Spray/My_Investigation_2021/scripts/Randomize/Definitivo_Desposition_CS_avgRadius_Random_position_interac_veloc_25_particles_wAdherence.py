# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2017 replay file
# Internal Version: 2016_09_27-18.54.59 126836
# Run by Magister12 on Fri Jul 31 17:05:57 2020
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
import random
import math
import numpy as np
import itertools

from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=228.392501831055, 
    height=132.946670532227)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup


# ----------------------- o ------------------------
# Definicion de funciones




#   Particles ---------------- PP ---------------------------
def copy_Particle(model_name, mother_particle_name, daughter_particle_name):
    p1 = mdb.models[model_name].parts[mother_particle_name]
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models[model_name].Part(name=daughter_particle_name, 
        objectToCopy=mdb.models[model_name].parts[mother_particle_name])
    session.viewports['Viewport: 1'].setValues(displayedObject=p)

def redefine_Radius_Particle(model_name, daughter_particle_name, radiuss):
    p = mdb.models[model_name].parts[daughter_particle_name]
    s = p.features['Solid revolve-1'].sketch
    mdb.models[model_name].ConstrainedSketch(name='__edit__', 
        objectToCopy=s)
    s2 = mdb.models[model_name].sketches['__edit__']
    g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
    s2.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s2, 
        upToFeature=p.features['Solid revolve-1'], filter=COPLANAR_EDGES)
    d[0].setValues(value=radiuss, )
    s2.unsetPrimaryObject()
    p = mdb.models[model_name].parts[daughter_particle_name]
    p.features['Solid revolve-1'].setValues(sketch=s2)
    del mdb.models[model_name].sketches['__edit__']
    p = mdb.models[model_name].parts[daughter_particle_name]
    p.regenerate()
    
def regenerate_Mesh_Particle(model_name, daughter_particle_name):
    p = mdb.models[model_name].parts[daughter_particle_name]
    p.generateMesh()
    
# NO USAAAAR    
# def redefine_Mass_Inertia(model_name, daughter_particle_name, radiuss):
    # p1 = mdb.models[model_name].parts[daughter_particle_name]
    # session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    # Masss = 3.85e-9 * 4.0/3.0*math.pi*radiuss**3.0
    # Inertiaa = 2.0/5.0 * Masss * radiuss**2.0
    # mdb.models[model_name].parts[daughter_particle_name].engineeringFeatures.inertias['Inertia_Particle_3D'].setValues(
        # mass=Masss, i11=Inertiaa, i22=Inertiaa, i33=Inertiaa)
    





#   Assemblies ----------------------- AA -------------------------
def create_Instance_Assembly(part_name, model_name):
    #Generar Instancia de Assembly
    a1 = mdb.models[model_name].rootAssembly
    p = mdb.models[model_name].parts[part_name]
    Instance_Name = part_name+'-1'
    a1.Instance(name=Instance_Name, part=p, dependent=ON)
    return Instance_Name
    
    # Recibe valores, y retorna un np.array() de dimension 1 fila, 3 columnas, con los valores del vector de traslacion randomizado
    # Los valores x_min, z_min debieran ser negativos
def generate_Vector_Translation_Random(x_min, x_max, y_min, y_max, z_min, z_max, radius_circle_impact_area_xz):
    yy = random.uniform(y_min, y_max)
    while True:
        xx = random.uniform(x_min, x_max)
        zz = random.uniform(z_min, z_max)
        # Condicion de que este dentro del circulo
        if xx**2.0 + zz**2.0 <= radius_circle_impact_area_xz**2.0:
            Vector_Translation = np.array([xx, yy, zz])
            break
    return Vector_Translation
    
    # Random solo en y
    # y_min, y_max: lo mismo que la funcion de arriba
    # radiuss = 0.00875
    # delta_separation_particles = 0.001
    # number_of_rows = 5
    # number_of_columns = 5
    # number_of_particles = 25
    # retorna un np.array de 25 filas, cada fila es un vector de traslacion, en las columnas estan las cordenadas de cada vector.
def generate_Vector_Translation_with_Patron(y_min, y_max, Radius_Particles, delta_separation_particles, number_of_rows, number_of_columns, number_of_particles):
    R = Radius_Particles
    delta = delta_separation_particles
    RR = R + delta / 2
    vectores = np.zeros((number_of_particles, 3))
    i = 0 # Recorre las particulas
    for zz in range(number_of_rows):
      for xx in range(number_of_columns):
        if zz % 2 == 0:
          the_factor = 2 * xx - 4
        else:
          if zz % 3 == 0:
            the_factor = 2 * xx - 5
          else:
            the_factor = 2 * xx - 3
        vectores[i, 0] = the_factor * (RR)
        vectores[i, 2] = (2 * zz - 4) * RR
        vectores[i, 1] = random.uniform(y_min, y_max)
        i = i + 1
    return vectores

    # vector_translation es un np.array
def translate_Instance_random(instance_name, model_name, vector_translation):
    #Mover la Instancia a una posicion random
    a1 = mdb.models[model_name].rootAssembly
    a1.translate(instanceList=(instance_name, ), vector=(vector_translation[0], vector_translation[1], vector_translation[2]))






#Functions to create Interactions with the Blank ------------------------------------------------------------------------
def copy_Interaction(model_name, mother_interaction_name, daughter_interaction_name):
    mdb.models[model_name].Interaction(
    name=daughter_interaction_name, 
    objectToCopy=mdb.models[model_name].interactions[mother_interaction_name], 
    toStepName='Initial')
    
def assign_Interaction(model_name, daughter_interaction_name, instance_involved): 
    a = mdb.models[model_name].rootAssembly
    region1=a.instances[instance_involved].surfaces['Master']
    mdb.models[model_name].interactions[daughter_interaction_name].setValues(
        master=region1, mechanicalConstraint=KINEMATIC, sliding=FINITE, 
        interactionProperty='IntProp-1', initialClearance=OMIT, datumAxis=None, 
        clearanceRegion=None)
    





# Functions to create Interactions between particles
# instance_involved_1 : String de la particula 1 involucrada
# instance_involved_2 : String de la particula 2 involucrada
# interaction_property_name : IntProp-2 (en string)
# created_interaction_name : P.e. entre particula 1 y 2: 'P1_P2_CS'
def create_and_Assign_Interaction_Between_Particles(model_name, instance_involved_1, instance_involved_2, interaction_property_name , created_interaction_name):
    a = mdb.models[model_name].rootAssembly
    region1=a.instances[instance_involved_1].surfaces['Master']
    a = mdb.models[model_name].rootAssembly
    region2=a.instances[instance_involved_2].surfaces['Master']
    mdb.models[model_name].SurfaceToSurfaceContactExp(
        name =created_interaction_name, createStepName='Initial', master = region1, 
        slave = region2, mechanicalConstraint=KINEMATIC, sliding=FINITE, 
        interactionProperty=interaction_property_name, initialClearance=OMIT, datumAxis=None, 
        clearanceRegion=None)
    #: The interaction "P1_P2_CS" has been created.






# Functions to create velocities of particles------------------------------------------------------------------------
def copy_Velocity_Particle(model_name, mother_velocity_name, daughter_velocity_name):
    mdb.models[model_name].PredefinedField(
        name=daughter_velocity_name, 
        objectToCopy=mdb.models[model_name].predefinedFields[mother_velocity_name], 
        toStepName='Initial')
    
    
def assign_Velocity_Particle(model_name, daughter_velocity_name, instance_involved):
    a = mdb.models[model_name].rootAssembly
    region = a.instances[instance_involved].sets['Particle_Section_Assignment']
    mdb.models[model_name].predefinedFields[daughter_velocity_name].setValues(
        region=region, velocity1=0.0, velocity2=-400000.0, velocity3=0.0, omega=0.0)





 # Functions to create Temperature of particles --------------------------------------------------------------------
 # mother_temperature_name = 'Particle_Temperature'
 # daughter_temperature_name = 'Particle<nro>_Temperature'
def copy_Temperature_Particle(model_name, mother_temperature_name, daughter_temperature_name):
     mdb.models[model_name].PredefinedField(
        name=daughter_temperature_name, 
        objectToCopy=mdb.models[model_name].predefinedFields[mother_temperature_name], 
        toStepName='Initial')
 
 # instance_involved = instancia que se le esta asignando la temperatura. Es un string
 # daughter_temperature_name = 'Particle<nro>_Temperature'
def assign_Temperature_Particle(model_name, daughter_temperature_name, instance_involved):
    a = mdb.models[model_name].rootAssembly
    region = a.instances[instance_involved].sets['Particle_Section_Assignment']
    mdb.models[model_name].predefinedFields[daughter_temperature_name].setValues(
        region=region)
        
        




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


model_name = 'My_Investigation_CS_25_Particles_Adherence'

executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
openMdb(
    pathName='D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\My_Investigation_2021/FOR_SCRIPTING_Particles/for_deposition/My_Investigation_for_scripting_particles_and_deposition.cae')
#: The model database "D:\Pipe\Tesis\ABAQUS_Various\CAEs\Cold_Spray_3D\Ghelichi_2014\CS_Ghelichi_2014_for_scripting_Particles/Ghelichi_2014_for_scripting_particles.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models[model_name].parts['Blank_3D_CS']
session.viewports['Viewport: 1'].setValues(displayedObject=p)



number_of_particles = 25

# Renaming model
new_model_name = 'My_Investigation_CS_' + str(number_of_particles) + 'Particles_Adherence'
mdb.models.changeKey(fromName=model_name, 
    toName=new_model_name)
model_name = new_model_name






# Particle Creation ------------------------------------- PC ------------------------------------------------
mother_particle_name = 'Particle_3D_CS'

for i in range(number_of_particles):
    if i == 0:  # Modificacion de la primera particula Madre
        radiuss = random.uniform(0.00875, 0.00875)
        redefine_Radius_Particle(model_name, mother_particle_name, radiuss)
        # regenerate_Mesh_Particle(model_name, mother_particle_name)
        # redefine_Mass_Inertia(model_name, mother_particle_name, radiuss) No debe usarse pues es Deformable
    else:  # Creacion de las demas particulas
        daughter_particle_name = 'Particle_3D_CS-' + str(i+1)
        radiuss = random.uniform(0.00875, 0.00875)
        # Generar la particula
        copy_Particle(model_name, mother_particle_name, daughter_particle_name)
        redefine_Radius_Particle(model_name, daughter_particle_name, radiuss)
        # regenerate_Mesh_Particle(model_name, daughter_particle_name)
        # redefine_Mass_Inertia(model_name, daughter_particle_name, radiuss) Este no debe usarse pues es Deformable
    








# Instances Creation ------------------------------------ IC -------------------------------------
x_min = 0.0
x_max = 0.0
z_min = 0.0
z_max = 0.0
y_min =  0.00925
y_max =  0.2
radius_circle_impact_area_xz = 0.05

Patron_Order        = True # Define si se utiliza orden con el patron o no. Si es False, se randomiza todo.
Radius_Particles    = 0.00875
delta_separation_particles = 0.001
number_of_rows      = 5
number_of_columns   = 5



# R = 0.00875
# delta = 0.001
# RR = R + delta / 2

# number_of_rows = 5
# number_of_columns = 5

# vectores = np.zeros((number_of_particles, 3))

# i = 0 # Recorre las particulas
# for zz in range(number_of_rows):
  # for xx in range(number_of_columns):
    # if zz % 2 == 0:
      # the_factor = 2 * xx - 4
    # else:
      # if zz % 3 == 0:
        # the_factor = 2 * xx - 5
      # else:
        # the_factor = 2 * xx - 3
    # vectores[i, 0] = the_factor * (RR)
    # vectores[i, 2] = (2 * zz - 4) * RR
    # i = i + 1



if Patron_Order == False:
    # Create first Instance
    instance_name = create_Instance_Assembly('Particle_3D_CS', model_name)
    vector_translation = generate_Vector_Translation_Random(x_min, x_max, y_min, y_max, z_min, z_max, radius_circle_impact_area_xz)
    translate_Instance_random(instance_name, model_name, vector_translation)

    # Create from second to the last Instance
    for i in range(number_of_particles - 1):
        instance_name = create_Instance_Assembly('Particle_3D_CS-'+str(i+2), model_name)
        vector_translation = generate_Vector_Translation_Random(x_min, x_max, y_min, y_max, z_min, z_max, radius_circle_impact_area_xz)
        translate_Instance_random(instance_name, model_name, vector_translation)
        
else:
    # Create first Instance
    instance_name = create_Instance_Assembly('Particle_3D_CS', model_name)
    vector_translation = generate_Vector_Translation_with_Patron(y_min, y_max, Radius_Particles, delta_separation_particles, number_of_rows, number_of_columns, number_of_particles)
    translate_Instance_random(instance_name, model_name, vector_translation[0])

    # Create from second to the last Instance
    for i in range(number_of_particles - 1):
        instance_name = create_Instance_Assembly('Particle_3D_CS-'+str(i+2), model_name)
        # vector_translation = generate_Vector_Translation_with_Patron(y_min, y_max, Radius_Particles, delta_separation_particles, number_of_rows, number_of_columns, number_of_particles)
        translate_Instance_random(instance_name, model_name, vector_translation[i+1])
    






# Interactions with Blank Creation --------------------------------IntC ----------------------------------------
mother_interaction_name = 'Blank_Particle1_CS'

# Create and assign Interactions with the substrate
for i in range(number_of_particles):
# The next lines can be omitted
    if i == 0:
        continue
    else:
        # end of possible omitted lines
        daughter_interaction_name = 'Blank_Particle' + str(i+1) + '_CS'
        instance_involved = 'Particle_3D_CS-' + str(i+1) + '-1'
        copy_Interaction(model_name, mother_interaction_name, daughter_interaction_name)
        assign_Interaction(model_name, daughter_interaction_name, instance_involved)






# Interactions Betweet Particles --------------------------------IntC ----------------------------------------

# Copy Interaction 1
# Se copia la IntProp-1 (con adherencia), en IntProp-2 y se retira la adherencia en esta ultima
# Esto se hace solo una vez
interaction_property_name = 'IntProp-2'
mdb.models[model_name].InteractionProperty(
    name=interaction_property_name, 
    objectToCopy=mdb.models[model_name].interactionProperties['IntProp-1'])
mdb.models[model_name].interactionProperties[interaction_property_name].tangentialBehavior.setValues(
    formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
    pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
    0.2, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
    fraction=0.005, elasticSlipStiffness=None)
mdb.models[model_name].interactionProperties[interaction_property_name].normalBehavior.setValues(
    pressureOverclosure=HARD, allowSeparation=ON, 
    constraintEnforcementMethod=DEFAULT)

# Asignar las interacciones entre particulas ------------------------------------ AIbP --------------------------------
array_particles = np.arange(1, number_of_particles + 1)
LL = []
combinations = itertools.combinations(array_particles, 2) # Se generan las combinaciones
for c in combinations:           # Se ponen las combinaciones en una lista
  LL.append(c)
combinations_array = np.array(LL)    # La lista se convierte en un array. Cada fila es una combinacion, cada columna es una particula (nro entero)

for fila in combinations_array:
    if fila[0] == 1:
        instance_involved_1 = 'Particle_3D_CS-' + str(fila[0])
        instance_involved_2 = 'Particle_3D_CS-' + str(fila[1]) + '-1'
    elif fila[1] == 1:
        instance_involved_1 = 'Particle_3D_CS-' + str(fila[0]) + '-1'
        instance_involved_2 = 'Particle_3D_CS-' + str(fila[1])
    else:
        instance_involved_1 = 'Particle_3D_CS-' + str(fila[0]) + '-1' 
        instance_involved_2 = 'Particle_3D_CS-' + str(fila[1]) + '-1'
    created_interaction_name = 'P' + instance_involved_1 + '_P' + instance_involved_2 + '_CS'
    create_and_Assign_Interaction_Between_Particles(model_name, instance_involved_1, instance_involved_2, interaction_property_name , created_interaction_name)









# Velocity Creation ----------------------------------- VC --------------------------------------
mother_velocity_name = 'Velocity_Particle1_3D_CS'

# Create and assign Velocities
for i in range(number_of_particles):
# The next lines can be omitted
    if i in range(1):
        continue
    else:
        # end of possible omitted lines
        daughter_velocity_name = 'Velocity_Particle' + str(i+1) + '_3D_CS'
        instance_involved = 'Particle_3D_CS-' + str(i+1) + '-1'
        copy_Velocity_Particle(model_name, mother_velocity_name, daughter_velocity_name)
        assign_Velocity_Particle(model_name, daughter_velocity_name, instance_involved)







# Temperature Creation ----------------------------------- TC --------------------------------------
mother_temperature_name = 'Particle_Temperature'

# Create and assign Velocities
for i in range(number_of_particles):
# The next lines can be omitted
    if i in range(1):
        continue
    else:
        # end of possible omitted lines
        daughter_temperature_name = 'Particle' + str(i+1) + '_Temperature'
        instance_involved = 'Particle_3D_CS-' + str(i+1) + '-1'
        copy_Temperature_Particle(model_name, mother_temperature_name, daughter_temperature_name)
        assign_Temperature_Particle(model_name, daughter_temperature_name, instance_involved)




for i in range(number_of_particles):
    if i == 0:
        particle_name_now = 'Particle_3D_CS'
    else:        
        particle_name_now = 'Particle_3D_CS-' + str(i+1)
    regenerate_Mesh_Particle(model_name, particle_name_now)



