# Bitacora de trabajo #

## Marzo 26 de 2019 ## 

### Actividades ###

#### ToDo ####
* Ver los siguientes enlaces:
  * https://pythonspot.com/threading/comment-page-1/
  * https://nitratine.net/blog/post/python-threading-basics/
  * https://www.python-course.eu/threads.php
  * https://www.shanelynn.ie/using-python-threading-for-multiple-results-queue/
  
#### Doing ####

* Hacer el main del experimento. Buscar la version antigua de disenoExperimental.py en el github. Aqui se hizo antes esto.
* Empezar la adaptacion del codigo.
  
#### Done ####
* Acabar de implentar la parte del trafico para el caso del ping.
* Agregar codigo que hagan lo siguiente:
  * **Obtenga los pid de los elementos de la red**: 
    * netstat.py: script que obtiene los puertos empleados por aplicaciones.
    * test3.py: script que obtiene los pids de los elementos de la red que se esta probando.
    * test_get_controller_pid.py: script que contiene el pid del controlador empleando la funcion netstat.
* **Realice un sniffing de la interfaz openFlow**: 
    * test_tshark.py: Sniffing de la interfaz OF.
* **Realizar un sniffing**:
    * test_bwm-ng.py: Sniffing de los puertos del switch.
* **Implementar la parte que mide la CPU de los elementos de red como una funcion**
* **Empezar a adaptar la funcion que mide la CPU gastada por los componenetes de la red en una funcion handler dentro de un timer**: Se hizo macheteramente usando excepciones en el hilo. Se recomienda para el caso no hacer uso de esta medida pues para todos los valores da 0 %.

### Informe de actividades ###

**Verificar el codigo que ya se encuentra listo o practicamente listo y anotarlo**

A continuacion se lista el codigo que se encuentra en etapa casi de culminacion:
1. controlador.py (Codificado, probado).
2. topologia.py (Codificado)
3. trafico.py (Codificado, probado)
   * Se modifico el tiempo de lanzamiento del ataque en lo que respecta al iperf.
   * Se modifico el tiempo de lanzamiento en lo que respecta al ping. 
4. unidadExperimental.py (Codificado, probado).
5. disenoExperimental.py (Codificado, probado). 
6. experimento.py (Codificado pero hay problemas en la prueba, esto pues se no se lanzan metricas con trafico normal y de ataque).

## Enlaces de interes ##
1. https://www.python-course.eu/forking.php
2. https://pymotw.com/2/multiprocessing/basics.html
3. https://appdividend.com/2019/02/06/python-os-module-tutorial-with-example/
4. https://docs.python.org/2/library/subprocess.html
5. https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
