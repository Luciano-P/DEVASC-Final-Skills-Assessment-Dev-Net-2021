###############################################################
# Este programa:
# - Pide al usuario que ingrese un token de acceso o use el token de acceso codificado.
# - Enumera las salas de Webex Teams del usuario.
# - Pregunta al usuario qué sala de Webex Teams debe supervisar las solicitudes "/location".
# - Supervisa cada segundo la sala de Webex Teams seleccionada en busca de mensajes "/location".
# - Descubre las coordenadas GPS para la "ubicación" usando la API de MapQuest.
# - Descubre la fecha y la hora del siguiente paso de ISS sobre la "ubicación" usando la API de ISS
# - Formatea y envía los resultados a la sala de Webex Teams.
#
# El estudiante debe:
# 1. Importar librerías para solicitudes, JSON y tiempo.
# 2. Complete la declaración if para solicitar al usuario el token de acceso de Webex Temas.
# 3. Proporcione la URL de la API de sala de Webex Temas.
# 4. Cree un bucle para imprimir el tipo y el título de cada sala.
# 5. Proporcione la URL de la API de mensajes de Webex Teams.
# 6. Proporcione la clave de consumidor de la API de MapQuest.
# 7. Proporcione la URL de la API de direcciones de MapQuest.
# 8. Proporcione los valores clave de MapQuest para obtener la latitud y la longitud.
# 9. Proporcione la URL de la API de tiempos de paso de ISS.
# 10. Proporcione los valores clave ISS del tiempo de ascenso y duración.
# 11. Convierta el valor del tiempo epoch de subida en una fecha y hora legibles por humanos.
# 12. Complete el código para formatear el mensaje de respuesta.
# 13. Complete el código para publicar el mensaje en la sala de Webex Teams.
###############################################################

# 1. Importar bibliotecas para solicitudes, JSON y tiempo.

import requests
import json
import time

# 2. Complete la declaración if para solicitar al usuario el token de acceso de Webex Teams.
choice = input ("¿Desea usar el token de Webex codificado? (y/n) ")

if choice == "n":
    AccessToken = "Bearer " + input("Ingrese su token de acceso: ")
elif choice == "y":
	AccessToken = "Bearer ODJkM2U3NTktNTQzZC00ZGVhLThhM2EtMDM4Y2IwOGM3NWM0MGI1MzU4NGEtMWEy_P0A1_1d36fb6a-16b5-4ac9-8965-bb2e5cb72e70"
else:
    print("Debe ingresar como respuesta: 'y' o 'n'")
    exit()

# 3. Proporcione la URL de la API de sala de Webex.
r = requests.get ("https://webexapis.com/v1/rooms",
                    headers = {"Authorization": AccessToken}
                )

#####################################################################################
# NO EDITAR NINGÚN BLOCK CON r.status_code
if not r.status_code == 200:
    raise Exception ("Respuesta incorrecta de la API de Webex Teams. Status code: {} Text: {}" .format (r.status_code, r.text))
######################################################################################

# 4. Cree un bucle para imprimir el tipo y el título de cada sala.
print ("List of rooms:")
rooms = r.json () ["items"]
for room in rooms:
    print("Type: " + room["type"] + " Name: " + str(room["title"]))

######################################################################################
#
# BUSCAR SALA DE EQUIPOS DE WEBEX PARA MONITOREAR
# - Busca el nombre de sala proporcionado por el usuario.
# - Si se encuentra, imprima el mensaje "found", de lo contrario imprime el error.
# - Almacena valores para su uso posterior por bot.
# NO EDITAR CÓDIGO EN ESTE BLOQUE
######################################################################################
#
while True:
    RoomNameToSearch = input ("¿Qué sala debe ser monitoreada para mensajes /location? ")
    RoomIDToGetMessages = None
    
    for room in rooms:
        if(room["title"].find(RoomNameToSearch) != -1):
            print ("Found rooms with the word " + RoomNameToSearch)
            print (room ["title"])
            RoomIDToGetMessages = room ["id"]
            RoomTitleToGetMessages = room ["title"]
            print ("sala encontrada:" + RoomTitleToGetMessages)
            break

    if (RoomIDToGetMessages == None):
        print ("Lo siento, no encontré ninguna sala con " + RoomNameToSearch +".")
        print ("Inténtelo de nuevo...")
    else:
        break

######################################################################################
# CÓDIGO BOT DE WEBEX TEAMS
# Inicia el bot de Webex para escuchar y responder a los mensajes /location.
######################################################################################
while True:
    time.sleep (1)
    GetParameters = {
                            "roomId": RoomIDToGetMessages,
                            "max": 1
                    }
# 5. Proporcione la URL de la API de mensajes de Webex.
    r = requests.get ("https://webexapis.com/v1/messages", 
                         params = GetParameters, 
                         headers = {"Authorization": AccessToken}
                    )

    if not r.status_code == 200:
        raise Exception ("Respuesta incorrecta de la API de Webex Teams. Status code: {} Texto: {}" .format (r.status_code, r.text))
    
    json_data = r.json ()
    if len (json_data ["items"]) == 0:
        raise Exception ("No hay mensajes en la sala.")
    
    messages = json_data ["items"]
    message = messages [0] ["text"]
    print("Received message: " + message)
    if message.find ("/") == 0:
        location = message [1:]
# 6. Proporcione la clave de consumidor de la API de MapQuest.
        print(location)
        MapsaPigetParameters = { 
                                "location": location, 
                                "key": "2GUmxpsfrkgf7g8hk28A3lkmMm3GBWHy"
                               }
# 7. Proporcione la URL de la API de direcciones de MapQuest.
        r = requests.get("http://www.mapquestapi.com/geocoding/v1/address", 
                             params = MapsaPigetParameters
                        )

        if not r.status_code == 200:
            raise Exception ("Respuesta incorrecta de la API de MapQuest. Status code: {} Texto: {}" .format (r.status_code, r.text))
        
        json_data = r.json()

        if not json_data ["info"] ["statuscode"] == 0:
            raise Exception ("Respuesta incorrecta de MapQuest API. Status code: {}" .format (r.statuscode))

        locationResults = json_data ["results"] [0] ["providedLocation"] ["location"]
        print ("Ubicación:" + locationResults)
		
# 8. Proporcione los valores clave de MapQuest para obtener la latitud y la longitud.
        locationLat = json_data ["results"][0]["locations"][0]["displayLatLng"]["lat"]
        locationLng = json_data ["results"][0]["locations"][0]["displayLatLng"]["lng"]
        print ("Localización coordenadas GPS:" + str (locationLat) + "," + str (locationLng))
        
        IssaPigetParameters = { 
                                "lat": locationLat, 
                                "lon": locationLng
                              }
# 9. Proporcione la URL de la API de tiempos de paso de ISS.
        r = requests.get("http://api.open-notify.org/iss-pass.json", 
                             params = IssaPigetParameters
                        )

        json_data = r.json()

        if not"response" in json_data:
            raise Exception ("Respuesta incorrecta de la API open-notify.org. Status code: {} Texto: {}" .format (r.status_code, r.text))

# 10. Proporcione los valores clave ISS del tiempo de espera y duración.
        risetimeinEpochSeconds = json_data ["response"][0]["risetime"]
        durationInSeconds = json_data ["response"][0]["duration"]
# 11. Convierta el valor de risetime epoch en una fecha y hora legible para humanos.
        risetimeInFormattedString = time.ctime(risetimeinEpochSeconds)
# 12. Complete el código para formatear el mensaje de respuesta.
# Ejemplo de resultado de un mensaje de respuesta: En Austin, Texas, la ISS sobrevolará el jue Jun 18 18:42:36 2020 durante 242 segundos.
        responseMessage = "En {} la ISS sobrevolará el {} durante {} segundos.".format(locationResults, risetimeInFormattedString, durationInSeconds)

        print ("Envío a Webex:" + responseMessage)

# 13. Complete el código para publicar el mensaje en la sala de Webex. 
        HttpHeaders = { 
                             "Authorization": AccessToken,
                             "Content-Type": "application/json"
                           }
        PostData = {
                            "roomId": RoomIDToGetMessages,
                            "text": responseMessage
                        }

        r = requests.post ("https://webexapis.com/v1/messages", 
                              data = json.dumps (PostData), 
                              headers= HttpHeaders
                         )
        if not r.status_code == 200:
            raise Exception ("Respuesta incorrecta de la API de Webex. Status code: {} Text: {}" .format (r.status_code, r.text))