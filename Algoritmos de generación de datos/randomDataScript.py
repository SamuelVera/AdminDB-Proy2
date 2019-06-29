import paho.mqtt.client as mqtt
import numpy as np
import json
import psycopg2 as pg2
import sys
import time as t
import datetime as dt
import random as r

##Selección de la fecha de la simulación
dia=1
mes=1
a=2019
salida=0
fecha=dt.datetime(a, mes, dia, 10)

################################ Estructuras auxiliares
existingSmartphones=[]
assignedSmartphones=[]
beaconsAcceso=[]
beaconsLocal=[]
sensores=[]
clientesInCC=[]
clientesOutOfCC=[]
camarasAcceso=[]
camarasLocal=[]
puertas=[]
puertasEmergencias=[]
locales=[]
mesas=[]
clientesInMesas=[]
clientesInLocales=[]
smartphonesQtty=0

    #Tópicos de MQTT
canalCamarasAcceso = "camarasAcceso/0"
canalCamarasLocal = "camarasLocal/0"
canalBeaconAccesoEntrada = "beaconAccesoEntrada/0"
canalBeaconAccesoSalida = "beaconAccesoSalida/0"
canalBeaconLocalEntrada = "beaconLocalEntrada/0"
canalBeaconLocalSalida = "beaconLocalSalida/0"
canalMesa = "mesa/0"
canalMesaSensorOcupado = "mesaSensorOcupado/0"
canalMesaSensorDescupado = "mesaSensorDesocupado/0"
canalFactura = "factura/0"
canalRegistrarSmartphone = "registrarSmartphone/0"

################
    #Clases auxiliares
class Cliente:
    def __init__(self, ci, sexo, edad, id_smartphone):
        self.ci=ci
        self.sexo=sexo
        self.edad=edad
        self.id_smartphone=id_smartphone

class DataMaestra:
    def __init__(self, id):
        self.id=id

class ClienteMqtt:
    def __init__(self, id):
        self.id=id
        self.mqtt_client=mqtt.Client()
    
    def connect_to_broker(self):
        self.mqtt_client.connect(host='127.0.0.1', port=1883)
        self.mqtt_client.on_connect=on_connect
        self.mqtt_client.loop_start()

################
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Conexión exitosa")
    else:
        print("Error de conexión, código: "+rc)

def connect_to_db():
        #Conexión a la db
    global conn1, conn2, conn3
    conn1 = pg2.connect(host='localhost', dbname="sambilproyectoventas", user="postgres", password="1234")
    conn2 = pg2.connect(host='localhost', dbname="sambilproyectoaccesos", user="postgres", password="1234")
    conn3 = pg2.connect(host='localhost', dbname="sambilproyectoferia", user="postgres", password="1234")
        #Cursor para operar
    global cur1, cur2, cur3
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cur3 = conn3.cursor()

#Instanciar smartphones existentes
def instanciateSmartphones():
    cur1.execute("SELECT id FROM smartphone ORDER BY id DESC;")
    aux = cur1.fetchall()
    for x in aux:
        if x==0:    
            global smartphonesQtty
            smartphonesQtty=x[0]
        existingSmartphones.append(x[0])

#Instanciar cámaras y conectarlas al broker
def instanciateCamaras():
    cur2.execute("SELECT id FROM camara;")
    aux = cur2.fetchall()
    for x in aux:
        toInsert=ClienteMqtt(x[0])
        toInsert.connect_to_broker()
        if(toInsert.id <= 3 ):
            camarasAcceso.append(toInsert)
        else:
            camarasLocal.append(toInsert)

#Instanciar cámaras y conectarlos al broker
def instanciateSensores():
    cur3.execute("SELECT id FROM sensormesa;")
    aux = cur3.fetchall()
    for x in aux:
        toInsert=ClienteMqtt(x[0])
        toInsert.connect_to_broker()
        sensores.append(toInsert)

#Instanciar beacons y conectarlos al broker
def instanciateBeacons():
    cur2.execute("SELECT id FROM beacon;")
    aux = cur2.fetchall()
    for x in aux:
        toInsert=ClienteMqtt(x[0])
        toInsert.connect_to_broker()
        if(x[0] <= 3):
            beaconsAcceso.append(toInsert)
        else:
            beaconsLocal.append(toInsert)

#Instanciar puertas
def instanciatePuertas():
    #Puertas normales
    cur2.execute("SELECT numero, emergencia FROM puerta;")
    aux = cur2.fetchall()
    for x in aux:
        toInsert=DataMaestra(x[0])
        #Es una puerta de emergencias
        if x[1] == True:
            puertasEmergencias.append(toInsert)
        #Es una puerta regular
        else:
            puertas.append(toInsert)

#Instanciar locales
def instanciateLocales():
    cur2.execute("SELECT id FROM local;")
    aux = cur2.fetchall()
    for x in aux:
        toInsert=DataMaestra(x[0])
        locales.append(toInsert)

#Instanciar mesas
def instanciateMesas():
    cur3.execute("SELECT id FROM mesa;")
    aux = cur3.fetchall()
    for x in aux:
        toInsert=DataMaestra(x[0])
        mesas.append(toInsert)

#Registro de un nuevo smartphone
def register_smartphone(smartphone):
    x={
        "id": (smartphone)
    }
    y=json.dumps(x)
    sensores[0].mqtt_client.publish(topic=canalRegistrarSmartphone,payload=y,qos=0)

#Publish al acceso por una puerta
def publish_access(camaraAcceso, cliente, puerta):
    minutes=r.randint(0,10)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "sexo": cliente.sexo,
        "edad": cliente.edad,
        "fechaacceso": str(fechaAcceso),
        "idpuerta": puerta.id,
    }
    y=json.dumps(x)
    camaraAcceso.mqtt_client.publish(topic=canalCamarasAcceso,payload=y,qos=0)

#Publicar salida por una puerta
def publish_salida_puerta(camaraAcceso, cliente, puerta):
    minutes=r.randint(45,59)
    fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "sexo": cliente.sexo,
        "edad": cliente.edad,
        "fechaAcceso": str(fechaSalida),
        "idpuerta": puerta.id,
    }
    y=json.dumps(x)
    camaraAcceso.mqtt_client.publish(topic=canalCamarasAcceso,payload=y,qos=0)

#Publish al comienzo de la estadia de alguien con smartphone
def publish_start_estadia(beaconEntrada, smartphone, puerta):
    minutes=r.randint(0,15)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idsmartphone": smartphone,
        "fechaentrada":str(fechaAcceso),
        "idpuertaentrada": puerta.id
    }
    y=json.dumps(x)
    beaconEntrada.mqtt_client.publish(topic=canalBeaconAccesoEntrada,payload=y,qos=0)

#Publish al salir un smartphone del centro comercial
def publish_finish_estadia(beaconSalida, smartphone, puerta, fecha):
    x={
        "idsmartphone": smartphone,
        "fechasalida": str(fecha),
        "idpuertasalida": puerta.id
    }
    y=json.dumps(x)
    beaconSalida.mqtt_client.publish(topic=canalBeaconAccesoSalida,payload=y,qos=0)

#Persona ingresa a una tienda
def publish_acceso_tienda_entrada(cliente, local, camara):
    minutes=r.randint(10,20)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "sexo": cliente.sexo,
        "edad": cliente.edad,
        "fechaacceso": str(fechaAcceso),
        "idlocal": local.id
    }
    y=json.dumps(x)
    camara.mqtt_client.publish(topic=canalCamarasLocal, payload=y, qos=0)

#Persona sale de una tienda
def publish_acceso_tienda_salida(cliente, local, camara):
    minutes=r.randint(21,40)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "sexo": cliente.sexo,
        "edad": cliente.edad,
        "fechaacceso": str(fechaAcceso),
        "idlocal": local.id
    }
    y=json.dumps(x)
    camara.mqtt_client.publish(topic=canalCamarasLocal, payload=y, qos=0)

#Smartphone ingresa a una tienda
def publish_recorrido_start(smartphone, local, beaconAcceso):
    minutes=r.randint(10,20)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idsmartphone": smartphone,
        "idlocal": local.id,
        "fechaentrada": str(fechaAcceso)
    }
    y=json.dumps(x)
    beaconAcceso.mqtt_client.publish(topic=canalBeaconLocalEntrada,payload=y,qos=0)

#Smartphone sale de una tienda
def publish_recorrido_finish(smartphone, local, beaconSalida):
    minutes=r.randint(21,40)
    fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idsmartphone": smartphone,
        "idlocal": local.id,
        "fechasalida": str(fechaSalida)
    }
    y=json.dumps(x)
    beaconSalida.mqtt_client.publish(topic=canalBeaconLocalSalida,payload=y,qos=0)
    
#Publicar una factura
def publish_factura(cliente, local, registradora):
    minutes=r.randint(25,40)
    fechaAcceso=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    smartphone=None
    if cliente.id_smartphone>0:
        smartphone=cliente.id_smartphone
    x={
        "cicomprador": cliente.ci,
        "idlocal": local.id,
        "monto": r.randint(10,1000),
        "fechacompra": str(fechaAcceso),
        "idsmartphone": smartphone
    }
    y=json.dumps(x)
    registradora.mqtt_client.publish(topic=canalFactura,payload=y,qos=0)

#Publicar que se ocupa una mesa
def publish_ocupa_mesa(mesa, sensor):
    minutes=r.randint(0,15)
    fechaEstado=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idmesa": mesa.id,
        "fechaestado": str(fechaEstado),
        "ocupado": True
    }
    y=json.dumps(x)
    sensor.mqtt_client.publish(topic=canalMesa,payload=y,qos=0)

#Publicar que se libera una mesa
def publish_libera_mesa(mesa, sensor):
    minutes=r.randint(20,45)
    fechaEstado=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idmesa": mesa.id,
        "fechaestado": str(fechaEstado),
        "ocupado": False
    }
    y=json.dumps(x)
    sensor.mqtt_client.publish(topic=canalMesa,payload=y,qos=0)

#Publica una nueva ocupación de mesa por un smartphone
def publish_sensor_ocupa_mesa(mesa, smartphone, sensor):
    minutes=r.randint(0,15)
    fechaOcupado=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idsmartphone": smartphone,
        "idmesa": mesa.id,
        "fechaocupado": str(fechaOcupado)
    }
    y=json.dumps(x)
    sensor.mqtt_client.publish(topic=canalMesaSensorOcupado,payload=y,qos=0)

#Publica que se descoupa la mesa
def publish_sensor_libera_mesa(mesa, smartphone, sensor):
    minutes=r.randint(20,45)
    fechaDesocupado=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
    x={
        "idsmartphone": smartphone,
        "idmesa": mesa.id,
        "fechadesocupado": str(fechaDesocupado),
    }
    y=json.dumps(x)
    sensor.mqtt_client.publish(topic=canalMesaSensorDescupado,payload=y,qos=0)

#Publicar una salida por una puerta de emergencia
def publish_salida_emergencia(cliente, puerta, camara, fecha):
    x={
        "sexo": cliente.sexo,
        "edad": cliente.edad,
        "fechaacceso": str(fecha),
        "idpuerta": puerta.id,
    }
    y=json.dumps(x)
    camara.mqtt_client.publish(topic=canalCamarasAcceso,payload=y,qos=0)

#Simulación
def simulacion():

    while salida > 0:
            #Ingreso de personas al comenzar una hora
        ingreso_personas()
            #Recorrido de las personas que están dentro del CC
        recorrido_personas()
            #Desocupado de mesas
        desocupan_mesas()
            #Salen de locales
        salen_de_local()
            #Checkeo para la salida de personas
        check_salida()

#Crear cliente
def create_cliente(ci):
        #Detección del sexo
    sexo = int(np.random.exponential(1.1))
    if sexo < 2:
        sexo = np.random.binomial(1,0.54)
    else:
        sexo = 2
        #¿Tiene smartphone o no?
    has_smartphone=r.randint(0,3)
        #Edad detectada por la cámara
    edad=int(np.random.normal(40,15))

    #No tiene smartphone
    if has_smartphone == 0:
        #Instanciación de cliente sin smartphone (smartphone_id=0)
        cliente=Cliente(ci,sexo,edad,0)
        clientesInCC.append(cliente)
    else:
        #Decisión de si es un nuevo smarphone o uno registrado previamente
        nuevoSmartphone = np.random.normal(0,1)
        
        #Smartphone registrado previamente
        if len(existingSmartphones) > 0 and nuevoSmartphone < 0.85:
            smartphone=existingSmartphones.pop(r.randint(1,len(existingSmartphones))-1)
            cliente=Cliente(ci,sexo,edad,smartphone)
            assignedSmartphones.append(smartphone)
            clientesInCC.append(cliente)
        
        #Nuevo smartphone registrado
        else:
            #Construcción del id
            global smartphonesQtty
            smartphonesQtty+=1
            smartphone=smartphonesQtty
            #Smartphones detectados en la ejecución
            assignedSmartphones.append(smartphone)
            cliente=Cliente(ci,sexo,edad,smartphone)
            clientesInCC.append(cliente)
            register_smartphone(smartphone)
            t.sleep(0.1)

    #Cámara que detecta el acceso
    camara=camarasAcceso[(r.randint(1,len(camarasAcceso))-1)]
    #Puerta por la que entra
    puerta=puertas[(r.randint(1,len(puertas))-1)]
    publish_access(camara, cliente, puerta)
    t.sleep(0.1)
    if cliente.id_smartphone > 0:
        #Si tiene smartphone el beacon inicia una estadia para el smartphone
        beacon=beaconsAcceso[(r.randint(1,len(beaconsAcceso))-1)]
        publish_start_estadia(beacon, cliente.id_smartphone, puerta)
        t.sleep(0.1)

#Ingreso de personas sleep
def ingreso_personas():
    #Solo entran antes de las 7:00 pm
    if fecha.hour < 19:
        #Cantidad de clientes a crear
        clientsToCreate = int(np.random.normal(7,1))
        print('Ingresan ',str(clientsToCreate))
        #Cédula de los clientes
        ci=10+len(clientesInCC)+len(clientesOutOfCC)
        while clientsToCreate > 0:
            #Creación del clientes
            create_cliente(ci)
            clientsToCreate=clientsToCreate-1
            ci+=1
                
        regresaGente = np.random.normal(0,1)
        #25% de las veces vuele a entrar un lote de gente
        if regresaGente < -0.67:
            usersToReturn = int(np.random.normal(6,1))
            #Hay usuarios para cubrir el lote que vuelve
            if usersToReturn < len(clientesOutOfCC):
                #Cantidad que vuelve usersToReturn-auxo
                auxo = int(usersToReturn/2)
                print('Vuelven a entrar ',str(auxo))
                while usersToReturn > auxo:
                    #Cliente que vuelve
                    cliente=clientesOutOfCC.pop(r.randint(1,len(clientesOutOfCC))-1)
                    #Actualización de las estructuras
                    clientesInCC.append(cliente)
                    usersToReturn=usersToReturn-1
                    #Cámara que detecta el acceso
                    camara=camarasAcceso[(r.randint(1,len(camarasAcceso))-1)]
                    #Puerta de acceso
                    puerta=puertas[(r.randint(1,len(puertas))-1)]
                    publish_access(camara, cliente, puerta)
                    t.sleep(0.1)
                    
                    #Si tiene smartphone hay una nueva estadía
                    if cliente.id_smartphone>0:
                        print(cliente.ci,' Tiene smartphone')
                        #Beacon que detecta la nueva estadía
                        beacon=beaconsAcceso[(r.randint(1,len(beaconsAcceso))-1)]
                        publish_start_estadia(beacon, cliente.id_smartphone, puerta)
                        t.sleep(0.1)

#Recorrido de las personas en el CC
def recorrido_personas():
    #Cantidad de clientes en el centro comercial
    print(len(clientesInCC))
    i=0
    while i<len(clientesInCC):
        decisionEmergencia = np.random.normal(0,1)
            #Salen por la puerta de emergencias un 3% de las veces
        if decisionEmergencia < -1.88:

            print('Sale por la puerta de emergencia')
            
            cliente=clientesInCC.pop(i)
            clientesOutOfCC.append(cliente)
            puerta=puertasEmergencias[r.randint(1,len(puertasEmergencias))-1]
            camara=camarasAcceso[r.randint(1,len(camarasAcceso))-1]
            minutes=r.randint(15,59)
            fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
            publish_salida_emergencia(cliente, puerta, camara, fechaSalida)
            
            if cliente.id_smartphone != 0:                
                minutes=r.randint(15,59)
                fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
                beacon=beaconsAcceso[(r.randint(1,len(beaconsAcceso))-1)]
                publish_finish_estadia(beacon, cliente.id_smartphone, puerta, fechaSalida)

        else:
            #Decide ocupar una mesa, ir a un local, salirse o no hacer nada
            decision=np.random.normal(0,1)

            #Decide ocupar mesa 19% de las veces
            if decision > 0.9:
                print('Ocupa una mesa')
                    #Se ocupa una mesa si hay mesas disponibles
                if len(mesas) > 0:

                    #Mesa ocupada
                    mesa=mesas.pop((r.randint(1,len(mesas)))-1)
                    
                    #Sensor de la mesa
                    sensor=sensores[((r.randint(1,len(sensores)))-1)]

                    publish_ocupa_mesa(mesa, sensor)
                    t.sleep(0.1)

                    #Cliente que ocupa la mesa
                    cliente=clientesInCC.pop(i)
                    clientesInMesas.append([cliente,mesa])

                    #Si tiene smartphone
                    if cliente.id_smartphone>0:
                        publish_sensor_ocupa_mesa(mesa, cliente.id_smartphone, sensor)
                        t.sleep(0.1)

                else: #No hay mesas disponibles

                    #Puede que se va a salir del cc porque no hay mesas
                    decisionSalir = np.random.normal(0,1)
                    #70% de las veces se sale del cc
                    if decisionSalir < 0.53:
                        salir_del_cc(i)
                    #El 30% de las veces no se sale
                    else:
                        i+=1
                
            #Decisión de salirse del centro comercial 28% de las veces
            elif decision < -0.6:
                salir_del_cc(i)

            #Decide entrar a una tienda o no hacer nada 53% de las veces
            else:
                decision2=np.random.normal(0,1)
                    #En este caso 76% de las veces entra a una tienda 
                if decision2 < 0.7:

                    print('Entra a una tienda')
                    #Local al que entra
                    local=locales[(r.randint(1,len(locales)))-1]
                    #Cámara que detecta la entrada
                    camara=camarasLocal[(r.randint(1,len(camarasLocal)))-1]
                    #Cliente que entra / Actualización de las estructuras de datos
                    cliente=clientesInCC.pop(i)
                    clientesInLocales.append([cliente, local])

                    publish_acceso_tienda_entrada(cliente, local, camara)
                    t.sleep(0.1)
                    
                    #Beacon detecta que entra un smartphone
                    if cliente.id_smartphone != 0:
                        beacon=beaconsLocal[(r.randint(1,len(beaconsLocal))-1)]
                        publish_recorrido_start(cliente.id_smartphone, local, beacon)
                        t.sleep(0.1)
                    
                #24% de las veces no hace nada
                else:
                    i+=1

#Un cliente sale del cc
def salir_del_cc(i):
    print('Se sale')

    #Cliente que se está saliendo
    cliente=clientesInCC.pop(i)
    clientesOutOfCC.append(cliente)

    #Camara que detecta el flujo de salida
    camara=camarasLocal[(r.randint(1,len(camarasLocal)))-1]
    #Puerta por la cual sale
    puerta=puertas[(r.randint(1,len(puertas)))-1]
    publish_salida_puerta(camara, cliente, puerta)
    t.sleep(0.1)
    
    #Si tiene smartphone
    if cliente.id_smartphone>0:
        #Beacon que detecta la salida
        beacon=beaconsAcceso[(r.randint(1,len(beaconsAcceso))-1)]
        minutes=r.randint(45,59)
        fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
        publish_finish_estadia(beacon, cliente.id_smartphone, puerta, fechaSalida)
        t.sleep(0.1)

#Personas que están en mesas y deciden pararse
def desocupan_mesas():
    i=0
    while i<len(clientesInMesas):

        decideLiberar=np.random.normal(0,1)
        #Libera la mesa 70% de las veces
        if decideLiberar<0.53:
            
            #Desocupa la mesa
            tupla=clientesInMesas.pop(i)
            #Cliente que desocupa la mesa
            cliente=tupla[0]
            clientesInCC.append(cliente)
            #Mesa desocupada
            mesa=tupla[1]
            #Mesa libre
            mesas.append(mesa)

            print(cliente.ci,' Desocupa la mesa ',mesa.id)
            #Sensor cambia el estado de la mesa
            sensor=sensores[((r.randint(1,len(sensores)))-1)]

            #Si tiene un smartphone
            if cliente.id_smartphone != 0:
                #Detecta que se para de la mesa
                print('TIENE SMARTPHONE')
                publish_sensor_libera_mesa(mesa, cliente.id_smartphone, sensor)
                t.sleep(0.1)

            #Se libera una mesa
            publish_libera_mesa(mesa, sensor)
            t.sleep(0.1)

        #No se para de la mesa 30% de las veces
        else:
            tupla=clientesInMesas[i]
            cliente=tupla[0]
            mesa=tupla[1]
            print(cliente.ci,' No desocupa la mesa ',mesa.id)
            i+=1

#Personas que están en locales y deciden salir
def salen_de_local():
    i=0
    while i<len(clientesInLocales):
        decisionSalirLocal=np.random.normal(0,1)
        #Decise salir del local 70% de las veces
        
        tupla=clientesInLocales[i]
        cliente=tupla[0]
        local=tupla[1]
        camara=camarasLocal[(r.randint(1,len(camarasLocal)))-1]

        #Decision de compra
        decisionCompra=r.randint(0,1)
        #Hace una compra
        if decisionCompra == 0:
            publish_factura(cliente, local, camara)
            t.sleep(0.1)
        
        #70% de las vecces sale del local
        if decisionSalirLocal<0.53:
            
            tupla=clientesInLocales.pop(i)
            #Cliente que sale
            cliente=tupla[0]
            clientesInCC.append(cliente)
            #Local del que sale
            local=tupla[1]
            print(cliente.ci,' Sale del local ',local.id)
            
            #Sale de la tienda
            publish_acceso_tienda_salida(cliente, local, camara)
            t.sleep(0.1)
                #Si tiene smartphone registra la salida
            if cliente.id_smartphone != 0:
                beacon=beaconsLocal[(r.randint(1,len(beaconsLocal))-1)]
                print('Tiene smartphone')
                publish_recorrido_finish(cliente.id_smartphone, local, beacon)
                t.sleep(0.1)
        #30% de las veces no sale del local
        else:
            print(cliente.ci,' Se mantiene en el local ',local.id)
            i+=1

#Salida del día
def check_salida():
    #Va avanzando el día
    global fecha
    #Avanza 1 hora
    fecha=dt.datetime(year=fecha.year,month=fecha.month,day=fecha.day,hour=(fecha.hour+1))
    print(fecha)
    t.sleep(0.5)
    #Si son más de las 9pm
    if fecha.hour > 21:
        #Días restantes de simulación
        global salida
        salida=salida-1
        #Avanza el día
        fecha=dt.datetime(year=fecha.year,month=fecha.month,day=(fecha.day+1),hour=10)
        print('Se acabó el día')
        print('Quedan ',salida,' días de simulación')

        #Salen los clientes que estaban en los locales
        print('Quedan ', len(clientesInLocales),' en los locales, van a salir')
        while len(clientesInLocales)>0:
            tupla=clientesInLocales.pop(0)
            #Cliente que sale
            cliente=tupla[0]
            #Sale del local pero sigue en el CC
            clientesInCC.append(cliente)
            #Local del que sale
            local=tupla[1]
            print(cliente.ci,' Sale del local ',local.id)
            #Cámara que detecta el flujo
            camara=camarasLocal[(r.randint(1,len(camarasLocal)))-1]        
            #Sale de la tienda
            publish_acceso_tienda_salida(cliente, local, camara)
            t.sleep(0.1)
            
            #Si tiene smartphone registra la salida
            if cliente.id_smartphone != 0:
                beacon=beaconsLocal[(r.randint(1,len(beaconsLocal))-1)]
                print('Tiene smartphone')
                publish_recorrido_finish(cliente.id_smartphone, local, beacon)
                t.sleep(0.1)

        #Cliente que están sentados en mesas
        print('Quedan ', len(clientesInMesas),' en las locales, van a desocuparlas')
        while len(clientesInMesas)>0:
            #Desocupa la mesa
            tupla=clientesInMesas.pop(0)
            #Cliente que desocupa la mesa
            cliente=tupla[0]
            #El cliente desocupa la mesa pero sigue en el CC
            clientesInCC.append(cliente)
            #Mesa desocupada
            mesa=tupla[1]
            #Mesa libre
            mesas.append(mesa)
            print(cliente.ci,' Desocupa la mesa ',mesa.id)
            sensor=sensores[((r.randint(1,len(sensores)))-1)]

            #Si tiene smartphone se detecta que se para
            if cliente.id_smartphone != 0:
                print('TIENE SMARTPHONE')
                publish_sensor_libera_mesa(mesa, cliente.id_smartphone, sensor)
                t.sleep(0.1)

            #Se libera una mesa
            publish_libera_mesa(mesa, sensor)
            t.sleep(0.1)
        
        #Ahora van a salir todos
        print('Aún hay ', len(clientesInCC),' personas en el CC, ahora saldrán')
        while len(clientesInCC)>0:
            #Cliente que sale
            cliente=clientesInCC.pop(0)
            #Cámara que detecta la salida
            camara=camarasAcceso[(r.randint(1,len(camarasAcceso))-1)]
            #Puerta por la cual sale
            puerta=puertas[(r.randint(1,len(puertas))-1)]
            publish_salida_puerta(camara, cliente, puerta)
            print('Sale ',cliente.ci)
            t.sleep(0.1)
            #Si tiene smartphone
            if cliente.id_smartphone != 0:
                print('Tiene smartphone')
                #Beacon que detecta
                beacon=beaconsAcceso[(r.randint(1,len(beaconsAcceso))-1)]
                minutes=r.randint(45,59)
                fechaSalida=dt.datetime(fecha.year, fecha.month, fecha.day, fecha.hour, minutes)
                publish_finish_estadia(beacon, cliente.id_smartphone, puerta, fechaSalida)
                t.sleep(0.1)
            #Actualización de estructuras de datos
            clientesOutOfCC.append(cliente)
        
        t.sleep(1)
            
def main():
    connect_to_db()
    ##Instanciación de la data maestra para la simulación
    instanciateSmartphones()
    instanciateCamaras()
    instanciateBeacons()
    instanciateSensores()
    instanciateLocales()
    instanciatePuertas()
    instanciateMesas()
    #Comienzo de la simulación
    simulacion()

if __name__=='__main__':
 
    try:
        dia = int((input("Ingrese el dia en el cual desee iniciar la simulacion: ")))
        while dia<=0 or dia>=15:
            dia = int((input("Ingrese un dia entre el 1 y el 15: ")))
        mes = int((input("Ingrese el numero del mes en el cual desee iniciar la simulacion: ")))
        while mes<=0 or mes>=13:
            mes = int((input("Ingrese el numero del mes válido: ")))
        salida = int((input("Ingrese la cantidad de dias que desea dure la simulacion: ")))
        while salida<=0 or salida>=11:
            salida = int((input("Ingrese una cantidad de dias entre 1 y 10: ")))
        fecha=dt.datetime(a, mes, dia, 10)
        main()
    except ValueError:
         print("Error: Solo se permiten valores enteros!")
    sys.exit(0)