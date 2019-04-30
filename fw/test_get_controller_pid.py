from netstat import netstat

# Nota: Ejecutar como superusuario

if __name__ == '__main__':
    port = 6653
    for conn in netstat():
        # print conn
        if str(6653) in conn[2]:
            print "PID del controlador:",conn[5]
        
        
