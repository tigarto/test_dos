import dexpy.factorial
import dexpy.power
import dexpy.alias
import pandas as pd
import numpy as np
from pyDOE import fullfact
import random


""" Configuracion de los parametros del disenho experimental"""

'''
Descripcion del experimento
1. Variables respuesta:
   -> BW: ancho de banda
   -> RTT_avg 
   -> PacketLoss
   ******* Por agregar (CPU, PACKET_IN, PACKET_OUT, FLOW_MOD, Rx..., Tx...)
2. Factores:
   -> Controlador: Ryu, POX
   -> Tipo de trafico: Normal, tasa fija, flooding
      - Normal (background): hping3 -c 6000 IP_V (...)
      - Flooding y spoofing: hping3 ...
3. Numero de tratamientos: 20 tratamientos: 2^2
4. Numero de replicas por tratamiento: 2.   
'''

# En el momento por cuestiones de test solo van a ser dos pruebas

def obtenerTratamientos(niveles):
    num_factores = len(niveles)
    niveles_factor = {}
    for k in niveles:
        niveles_factor[k] = len(niveles[k])
    tratamientos = fullfact(niveles_factor.values())    
    return tratamientos

def codificarTratamientos(niveles):
    factores = niveles.keys()
    tr = obtenerTratamientos(niveles)
    tr = tr.astype(int)
    tr_cod = tr.astype(str)
    num_rows = tr.shape[0]
    i = 0
    index_fac = 0
    index_row = 0
    k = 0
    for e in np.nditer(tr, order='F'): 
        i += 1      
        tr_cod[index_row][index_fac] = niveles[factores[index_fac]][e]
        index_row += 1
        if i%num_rows == 0:
            index_row = 0
            index_fac += 1

        
        
    return tr_cod

def obtenerNumeroTratamientos(tratamientos):
    return tratamientos.shape[0]

def crearMatrixReplicas(numTratamientos,numReplicasPorTratamiento):
    random.seed() # Semilla para la aleatorizacion para las pruebas
    total_tests = np.arange(1,numTratamientos*numReplicasPorTratamiento + 1) # Lista ordenada de acuerdo al
                                                                             # numero total de replicas
    random.shuffle(total_tests) # Barajando la lista para aleatorizar el orden de las pruebas
    matrixReplicas = total_tests.reshape(numTratamientos,numReplicasPorTratamiento) # Generando la matrix a partir de la lista
    return matrixReplicas


def definirOrdenTratamientos(matrixReplicas,tratamientos):
    ordenTratamientos = []
    for rep in range(1,matrixReplicas.shape[0]*matrixReplicas.shape[1] + 1):
        index = np.where(matrixReplicas==rep)
        rep += 1
        E = tratamientos[index[0]][0].tolist()
        ordenTratamientos.append(E)
    return ordenTratamientos
        

if __name__ == "__main__":
    print("Ensayo")
    niveles = { 'controlador': ['ryu','pox'],
            'trafico': ['normal','ataque1','ataque2']
    }
    
    tr = obtenerTratamientos(niveles)
    print(tr)
    tr_cod = codificarTratamientos(niveles)
    print(tr_cod)
    n_tr = obtenerNumeroTratamientos(tr_cod)
    print(n_tr)
    m = crearMatrixReplicas(n_tr,3)
    print(m)
    ot = definirOrdenTratamientos(m,tr_cod)
    print(ot)
    
    print("*********************************************")

    niveles2 = { 'controlador': ['ryu','pox'],
                 'trafico': ['normal','ataque1','ataque2'],
                 'topologia':['topo1','topo2']
               }
    tr2 = obtenerTratamientos(niveles2)
    print(tr2)
    tr2_cod = codificarTratamientos(niveles2)
    print(tr2_cod)
    n_tr2 = obtenerNumeroTratamientos(tr2_cod)
    print(n_tr2)
    m2 = crearMatrixReplicas(n_tr,2)
    print(m2)
    ot2 = definirOrdenTratamientos(m2,tr2_cod)
    print(ot2)









