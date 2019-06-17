import json
import psycopg2 as pg2
import sys
import datetime as dt
import paho.mqtt.client as mqtt
import random as r

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
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Conexión exitosa")
    else:
        print("Error de conexión, código: "+rc)

def connect_to_db():
        #Conexión a la db
    global conn 
    conn = pg2.connect(host='localhost', dbname="sambilproyecto", user="postgres", password="1234")

def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        r.randint(0,255),
        r.randint(0,255),
        r.randint(0,255),
        r.randint(0,255),
        r.randint(0,255),
        r.randint(0,255)
    )

#Insertar smartphone
def insert_smartphone(smartphone):
    macaddress=rand_mac()
    with conn, conn.cursor() as cur:
        cur.execute('''
            INSERT INTO smartphone(id, macaddress)
            VALUES(%s,%s);
        ''',(smartphone["id"],macaddress))

#Insertar flujo por la puerta
def insert_camara_access(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO accesoentrada(sexo, edad, fechaacceso, idpuerta)
            VALUES(%s,%s,%s,%s);
        '''
        cur.execute(query,(data["sexo"],data["edad"],data["fechaacceso"],data["idpuerta"]))

#Iniciar nueva estadía
def insert_new_estadia(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO estadia(idsmartphone, fechaentrada, idpuertaentrada)
            VALUES(%s,%s,%s);
        '''
        cur.execute(query,(data["idsmartphone"],data["fechaentrada"],data["idpuertaentrada"]))

#Finaliza una estadia
def finish_estadia(data):
    with conn, conn.cursor() as cur:
        query='''
            UPDATE estadia 
            SET fechasalida=%s, idpuertasalida=%s
            WHERE id = (
                SELECT id FROM estadia
                WHERE idsmartphone=%s AND fechasalida IS NULL
                ORDER BY fechaentrada DESC
                LIMIT 1
            );
        '''
        cur.execute(query,(data["fechasalida"],data["idpuertasalida"],data["idsmartphone"]))

#Inserta flujo por una tienda
def insert_camara_local(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO accesolocal (sexo, edad, fechaacceso, idlocal)
            VALUES (%s,%s,%s,%s);
        '''
        cur.execute(query,(data["sexo"],data["edad"],data["fechaacceso"],data["idlocal"]))

#Iniciar nueva estadía en una tienda
def insert_new_recorrido(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO recorrido(idsmartphone, idlocal, fechaentrada)
            VALUES(%s,%s,%s);
        '''
        cur.execute(query,(data["idsmartphone"],data["idlocal"],data["fechaentrada"]))

#Finalizar una estadía en una tienda
def finish_recorrido(data):
    with conn, conn.cursor() as cur:
        query='''
            UPDATE recorrido
            SET fechasalida=%s
            WHERE id = ( 
                SELECT id FROM recorrido 
                WHERE idsmartphone=%s AND idlocal=%s AND fechasalida IS NULL 
                ORDER BY fechaentrada DESC
                LIMIT 1
            );
        '''
        cur.execute(query,(data["fechasalida"],data["idsmartphone"],data["idlocal"]))

#Insertar una nueva factura
def insert_new_factura(data):
    if data["idsmartphone"]==0:
        with conn, conn.cursor() as cur:
            query='''
                INSERT INTO factura (cicomprador, idlocal, monto, fechacompra)
                VALUES(%s,%s,%s,%s);
            '''
            cur.execute(query,(data["cicomprador"],data["idlocal"],data["monto"],data["fechacompra"])) 
    else:
        with conn, conn.cursor() as cur:
            query='''
                INSERT INTO factura (cicomprador, idlocal, monto, fechacompra, idsmartphone)
                VALUES(%s,%s,%s,%s,%s);
            ''' 
            cur.execute(query,(data["cicomprador"],data["idlocal"],data["monto"],data["fechacompra"],data["idsmartphone"]))

#Insertar un nuevo estado de una mesa
def insert_mesa_estado(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO estadomesa(idmesa, fechaestado, ocupado)
            VALUES(%s,%s,%s);
        '''
        cur.execute(query,(data["idmesa"],data["fechaestado"],data["ocupado"]))

#Insertar un nuevo monitoreo de mesa
def start_mesa_ocupacion(data):
    with conn, conn.cursor() as cur:
        query='''
            INSERT INTO monitoreomesa(idsmartphone, idmesa, fechaocupado)
            VALUES(%s,%s,%s);
        '''
        cur.execute(query,(data["idsmartphone"],data["idmesa"],data["fechaocupado"]))

#Finalizar una ocupación de una mesa
def finish_mesa_ocupacion(data):
    with conn, conn.cursor() as cur:
        query='''
            UPDATE monitoreomesa
            SET fechadesocupado=%s
            WHERE id = (
                SELECT id FROM monitoreomesa 
                WHERE idmesa=%s AND idsmartphone=%s AND fechadesocupado IS NULL
                ORDER BY fechaocupado DESC
                LIMIT 1
            );
        '''
        cur.execute(query,(data["fechadesocupado"],data["idmesa"],data["idsmartphone"]))

def on_message(client, userdata, message):
    msg_decode=message.payload.decode("utf-8")
    print(message.topic)
    y=json.loads(msg_decode)
    print(y)
    if message.topic == canalRegistrarSmartphone:
        insert_smartphone(y)
    if message.topic == canalCamarasAcceso:
        insert_camara_access(y)
    if message.topic == canalBeaconAccesoEntrada:
        insert_new_estadia(y)
    if message.topic == canalBeaconAccesoSalida:
        finish_estadia(y)
    if message.topic == canalCamarasLocal:
        insert_camara_local(y)
    if message.topic == canalBeaconLocalEntrada:
        insert_new_recorrido(y)
    if message.topic == canalBeaconLocalSalida:
        finish_recorrido(y)
    if message.topic == canalFactura:
        insert_new_factura(y)
    if message.topic == canalMesa:
        insert_mesa_estado(y)
    if message.topic == canalMesaSensorOcupado:
        start_mesa_ocupacion(y)
    if message.topic == canalMesaSensorDescupado:
        finish_mesa_ocupacion(y)
    conn.commit()

def main():

    connect_to_db()

        #Instanciación
    cliente=mqtt.Client(client_id="sub")

        #Set de callbacks
    cliente.on_connect=on_connect
    cliente.on_message=on_message

        #Conexiones
    cliente.connect(host="127.0.0.1", port=1883)

        #Suscribirse
    cliente.subscribe(topic=canalBeaconAccesoEntrada, qos=0)
    cliente.subscribe(topic=canalBeaconAccesoSalida, qos=0)
    cliente.subscribe(topic=canalBeaconLocalEntrada, qos=0)
    cliente.subscribe(topic=canalBeaconLocalSalida, qos=0)

    cliente.subscribe(topic=canalCamarasAcceso, qos=0)
    cliente.subscribe(topic=canalCamarasLocal, qos=0)

    cliente.subscribe(topic=canalMesa, qos=0)
    cliente.subscribe(topic=canalMesaSensorOcupado, qos=0)
    cliente.subscribe(topic=canalMesaSensorDescupado, qos=0)

    cliente.subscribe(topic=canalFactura, qos=0)
    cliente.subscribe(topic=canalRegistrarSmartphone, qos=0)

        #Activación de callbacks
    cliente.loop_forever()

if __name__=='__main__':
    main()
    sys.exit(0)