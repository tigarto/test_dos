import psutil
import subprocess
from netstat import netstat


"""
sudo ryu-manager --verbose simple_switch_13.py ofctl_rest.py


sudo mn --topo=single,3 --mac --switch=ovsk,protocols=OpenFlow13 --controller=remote,ip=127.0.0.1:6653  --link=tc,bw=100 
"""

pl = subprocess.Popen(['ps', '-ax','-o','pid,cmd'], stdout=subprocess.PIPE).communicate()[0]
lines = pl.split('\n')
mininet_lines = []
for l in lines:
    if "mininet" in l:
        mininet_lines.append(l)
    

print mininet_lines
dicProcesos = {}
for p in mininet_lines:
    l = p.split()
    if ("h" in l[-1]) or ("s" in l[-1]):        
        # Agregando hosts y el swith
        node = l[-1]
        dicProcesos[node[node.find(':')+1:]] = int(l[0])

# Agregando el controlador
port = 6653
for conn in netstat():
    # print conn
    if str(6653) in conn[2] and ('0.0.0.0' in conn[2]):
        dicProcesos['c0'] = int(conn[5]) 

procesos = []
for k in dicProcesos:
    p = psutil.Process(dicProcesos[k])
    dic_attr = p.as_dict(attrs=['pid', 'name', 'cpu_percent'])
    print(k,dic_attr['pid'],dic_attr['cpu_percent'])







   