# hevy api manifiesto

## Información de entrada

* La informacion de esta captura se utilizará para alimentar un archivo JSON para capturar las rutinas en la aplicacion Hevy.
* El contendo generado sera un archivo JSON
* pregunta el valor actual de new_routine_folder_id
* El objeto JSON debe tener la siguiente estructura:
{
  "routine": {
    "title": "”,
    "folder_id": {{new_routine_folder_id}},
    "exercises": [
      {
        "exercise_template_id": "",
        "superset_id": null,
        "rest_seconds": 60,
        "notes": "",
        "sets": [
          {
            "type": "normal",
            "weight_kg": 100,
            "reps": 10,
            "distance_meters": null,
            "duration_seconds": null,
            "custom_metric": null
          }
        ]
      }
    ]
  }
}

### Consideraciones

* El nombre de la rutina siempre empieza con “Día ”
* “Combinación” es un “superset”, usualmente de los 2 ejercicios siguientes.
* “Triserie” también es un superset, pero de los 3 ejercicios siguientes.
* “Indvidual “ es solo un ejercicio, significa que este ejercicio no forma parte del superset anterior.
* Los ejercicios vienen numeros (ej. ejercicio 1 - , ejercicio 2) omite esta información.
* En el primer renglón viene la información detallando numero de series y repeticiones (ej. Ejercicio 2 - 3x12-15rep. (incremento de peso)) esta información se debera guardar tal cual en la llave “notes”
* En el segundo renglón viene el nombre del ejercicio (util para traducir al ingles y encontrar el “exercise_template_id”) .

### Reglas

* No debes asumir ids si no encuentras equivalencias.
* No debes generar ids placeholders, deja el valor vacio para detectar rapidamente que falta ese valor.
* No pongas valores de memoria.
* Muestrame lo siguiente luego de que te entrega la informacion:
  * Tabla de equivalencias y IDs (ejercicio original, equivalente en ingles, id asignada)
  * listado ejercicios pendientes de ID
* Despues de verificar el listado de ejercicios pendientes de ID, te indicaré en el mismo orden el ID correspondiente a cada uno.
* Con esta información nueva, genera el archivo JSON solicitado.
* Si no hay ejercicios pendientes de id, siempre genera el json sin necesidad de confirmacion
* Despues de darte ids faltantes, genera el json sin necesidad de confirmacion

## Preferencias en rutinas

* 4 x 12 rep significa 4 series y 12 repeticiones cada una.
* 3 x 12-15 rep significa 3 series de 12 a 15 repeticiones. Utiliza siempre el numero más alto, quedaria en 3 series de 15 repeticiones.
* 1 vuelta x sistema asc/des (6, 8, 10, 12, + 12, 10, 8, 6 rep.) significa que seran varias series seguidas. Primera serie de 6 repeticiones, segunda serie de 8, tercera de 10, cuarta de 12, quinta de 12, sexta de 10, septima de 8 y finalmente una ultima serie de 6 repeticiones. Las series 2, 3 y 4 marcalas como dropsets.
* 2 x sistema exahustivo (1 rep. + 1 seg. en tensión; 2 rep + 2 seg en tensión; …. Nivel 6) significa que nivel 6 es el numero maximo de series y repeticiones. En este caso seran 6 series, incrementando las repeticiones cada serie. 1 serie 1 repeticion.
* En rutinas no Core, el total de series debe de ser las indicadas y además sumando la serie de calentamiento. Es decir, si la rutina dice 4 x 12, son 5 series ( 1 tipo “warmup”, 4 tipo “normal”)
* La duracion predeterminada del tiempo de recuperacion es de 1 minuto para rutinas que no sean de Core.
* Cuando hagas un super set, ponle rest_seconds de 0 a todos los ejercicios excepto al ultimo ejercicio del set, a ese ponle 120 segundos.
* Cuando el nombre de un ejercicio incluya “individual”,  “alternado”, “barra olimpica”, “barra z”, “pronado”, “supino”, “neutro”, “sentado”, “(con cuerda)” anexa esta información como parte de las notas en la propiedad "notes” pero conservando la info de repeticiones ej. “3x12-15rep. (incremento de peso) alternado”
* Cuando un ejercicio de mancuernas diga “individual”, duplica el numero de repeticiones, es decir, 3x12-15rep. pasaria a tener 30 repeticiones.
* Cuando el nombre del ejercicio incluya Adduction, anexar en propiedad notes “cierre piernas”. Cuando el nombre del ejerjecicio incluya Abduction, anexad “abre piernas”
* Cuando un ejercicio de press no especifique mancuerna, es con barra.
* Cuando la descripcion del ejercicio indique “sistema bulgaro” y detalle el tiempo de recuperacion 10-30seg, modificar el rest_seconds a 30 segundos.
* Cuando la rutina sea de Core, usa rest_seconds de 20 segundos en todos los ejercicios.
* Cuando la rutina sea de Core, usa 2 series normales por ejercicio.
* Cuando la descripcion del ejercicio indique “1 vuelta × sistema 21 rep.” significa 3 series de 7 repeticiones.
* Cuando la descripcion del ejercicio indique “cluster” significa 30 segundos de descanso entre series, minimo 3 series 6 repeticiones.
* Si el nombre de la rutina incluye un grupo muscular + Core (ej. “ESPALDA + CORE”), NO aplicar regla global de Core por título; mantener rest_seconds en 60 salvo reglas explícitas (ej. cluster).

### Los ejercicios

* Los ejercicios dentro de la propiedad "exercises" no llevan nombre, el valor clave es “exercise_template_id”, no incluir ninguna llave como “title” o “name” en este objeto
* "exercise_template_id" solo puede contener una id alfanumerica, jamas una frase o palabras comunes.
* Obtener el exercise_template_id traduciendo el nombre en español del ejercicio a ingles, y encontrar el valor equivalente en el schema ( ej. press de pecho en banca plana -> Bench Press (Barbell)).
* En rutinas no Core, el descanso default es de 60 segundos, rest_seconds = 60.
* En “notes” van las notas

### Los sets

* En rutinas no Core, crea al inicio de sets un set del tipo warmup de 12 repeticiones.
* En rutinas Core, no agregar set warmup.

## Preferencias en equivalencias de ejercicios

* Evita el uso de coincidencias parciales en los siguientes ejercicios definidos por mi, sigue al pie de la letra las indicaciones

Si la rutina es de Core, estas son las reglas:

* 2 series
* Usar 20 segundos de descanso en TODOS los ejercicios de la rutina Core
* No usar serie warmup
* 30 segundos objetivo de cada ejercicio de tiempo, “duration_seconds": 30. Solo cuando te lo indique yo mismo que el ejercicio es de tiempo.
