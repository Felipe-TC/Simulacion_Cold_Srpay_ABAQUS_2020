# Este codigo busca mostrar la randomizacion de particulas en 3D.
# Se usa en un .CAE especifico. No es un codigo generalizado. Les puede servir para ver el algoritmo.

# ---------------------------------------- o -----------------------------------

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
    s = p.features['3D Analytic rigid shell-1'].sketch
    mdb.models[model_name].ConstrainedSketch(
        name='__edit__', objectToCopy=s)
    s2 = mdb.models[model_name].sketches['__edit__']
    g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
    s2.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s2, 
        upToFeature=p.features['3D Analytic rigid shell-1'], filter=COPLANAR_EDGES)
    d[0].setValues(value=radiuss, )
    s2.unsetPrimaryObject()
    p = mdb.models[model_name].parts[daughter_particle_name]
    p.features['3D Analytic rigid shell-1'].setValues(sketch=s2)
    del mdb.models[model_name].sketches['__edit__']
    p = mdb.models[model_name].parts[daughter_particle_name]
    p.regenerate()
    
    
def redefine_Mass_Inertia(model_name, daughter_particle_name, radiuss):
    p1 = mdb.models[model_name].parts[daughter_particle_name]
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    Masss = 3.85e-9 * 4.0/3.0*math.pi*radiuss**3.0
    Inertiaa = 2.0/5.0 * Masss * radiuss**2.0
    mdb.models[model_name].parts[daughter_particle_name].engineeringFeatures.inertias['Inertia_Particle_3D'].setValues(
        mass=Masss, i11=Inertiaa, i22=Inertiaa, i33=Inertiaa)
    





#   Assemblies ----------------------- AA -------------------------
def create_Instance_Assembly(part_name, model_name):
    #Generar Instancia de Assembly
    a1 = mdb.models[model_name].rootAssembly
    p = mdb.models[model_name].parts[part_name]
    Instance_Name = part_name+'-1'
    a1.Instance(name=Instance_Name, part=p, dependent=ON)
    return Instance_Name
    
def translate_Instance_random(instance_name, model_name):
    #Mover la Instancia a una posicion random
    a1 = mdb.models[model_name].rootAssembly
    a1.translate(instanceList=(instance_name, ), vector=(random.uniform(-0.3, 0.3), random.uniform(0.305, 3.005), random.uniform(-0.3, 0.3)))






#Functions to create Interactions ------------------------------------------------------------------------
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
    




# Functions to create velocities of particles------------------------------------------------------------------------
def copy_Velocity_Particle(model_name, mother_velocity_name, daughter_velocity_name):
    mdb.models[model_name].PredefinedField(
        name=daughter_velocity_name, 
        objectToCopy=mdb.models[model_name].predefinedFields[mother_velocity_name], 
        toStepName='Initial')
    
    
def assign_Velocity_Particle(model_name, daughter_velocity_name, instance_involved):
    a = mdb.models[model_name].rootAssembly
    region = a.instances[instance_involved].sets['Set-1']
    mdb.models[model_name].predefinedFields[daughter_velocity_name].setValues(
        region=region, velocity1=0.0, velocity2=-34600.0, velocity3=0.0, omega=0.0)
        



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


executeOnCaeStartup()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
Mdb()
#: A new model database has been created.
#: The model "Model-1" has been created.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
openMdb(
    pathName='D:/Pipe/Tesis/ABAQUS_Various/CAEs/Shot_Peening_3D/For_Scripting_correcto/For_Scripting_Corregido_Gariepy/for_scripting_3D_Correcciones_based_on_Gariepy_2011.cae')
#: The model database "D:\Pipe\Tesis\ABAQUS_Various\CAEs\For_Scripting_Corregido_Gariepy\for_scripting_3D_Correcciones_based_on_Gariepy_2011.cae" has been opened.
session.viewports['Viewport: 1'].setValues(displayedObject=None)
p = mdb.models['Shot_3D_CORRECCIONES_15_Particles'].parts['Blank']
session.viewports['Viewport: 1'].setValues(displayedObject=p)



model_name = 'Shot_3D_CORRECCIONES_15_Particles'
number_of_particles = 15







# Particle Creation ------------------------------------- PC ------------------------------------------------
mother_particle_name = 'Particle_3D'

for i in range(number_of_particles):
    if i == 0:  # Modificacion de la primera particula Madre
        radiuss = random.uniform(0.2125, 0.3)
        redefine_Radius_Particle(model_name, mother_particle_name, radiuss)
        redefine_Mass_Inertia(model_name, mother_particle_name, radiuss)
    else:  # Creacion de las demas particulas
        daughter_particle_name = 'Particle_3D-' + str(i+1)
        radiuss = random.uniform(0.2125, 0.3)
        # Generar la particula
        copy_Particle(model_name, mother_particle_name, daughter_particle_name)
        redefine_Radius_Particle(model_name, daughter_particle_name, radiuss)
        redefine_Mass_Inertia(model_name, daughter_particle_name, radiuss)
    








# Instances Creation ------------------------------------ IC -------------------------------------
# Create first Instance
instance_name = create_Instance_Assembly('Particle_3D', model_name)
translate_Instance_random(instance_name, model_name)

# Create from second to the last Instance
for i in range(number_of_particles - 1):
    instance_name = create_Instance_Assembly('Particle_3D-'+str(i+2), model_name)
    translate_Instance_random(instance_name, model_name)







# Interactions Creation --------------------------------IntC ----------------------------------------
mother_interaction_name = 'Prticle1_Blank_3D'

# Create and assign Interactions
for i in range(number_of_particles):
# The next lines can be omitted
    if i in range(3):
        continue
    else:
        # end of possible omitted lines
        daughter_interaction_name = 'Prticle' + str(i+1) + '_Blank_3D'
        instance_involved = 'Particle_3D-' + str(i+1) + '-1'
        copy_Interaction(model_name, mother_interaction_name, daughter_interaction_name)
        assign_Interaction(model_name, daughter_interaction_name, instance_involved)








# Velocity Creation ----------------------------------- VC --------------------------------------
mother_velocity_name = 'Velocity_Particle1_3D'

# Create and assign Velocities
for i in range(number_of_particles):
# The next lines can be omitted
    if i in range(1):
        continue
    else:
        # end of possible omitted lines
        daughter_velocity_name = 'Velocity_Particle' + str(i+1) + '_3D'
        instance_involved = 'Particle_3D-' + str(i+1) + '-1'
        copy_Velocity_Particle(model_name, mother_velocity_name, daughter_velocity_name)
        assign_Velocity_Particle(model_name, daughter_velocity_name, instance_involved)

