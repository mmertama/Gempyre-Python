import sys
import os
import subprocess
import platform
import shlex

import Gempyre
from Gempyre_utils import resource

name = os.path.join(os.path.dirname(sys.argv[0]), "python_test_2.html")
map, names = resource.from_file(name)

ui = Gempyre.Ui(map, names[name])

header = Gempyre.Element(ui, "header");
Gempyre.Element(ui, "th", header).set_html("Name")
Gempyre.Element(ui, "th", header).set_html("Info")

name = list()

name.append(["Architecture", platform.architecture()[0]])
name.append(["Machine", platform.machine()])
name.append(["Node", platform.node()])
name.append(["System", platform.system()])

info = Gempyre.Element(ui, "info")
for n in name:
    h = Gempyre.Element(ui, "tr", info)
    Gempyre.Element(ui, "td", h).set_html(n[0])
    Gempyre.Element(ui, "td", h).set_html(n[1])
    
input = Gempyre.Element(ui, "command_line")
output = Gempyre.Element(ui, "output")

def do_run(ev):
    global input
    global output
    value = input.values()
    if not value or len(value['value']) == 0:
        return
    command_line = shlex.split(value['value'])
    out = subprocess.run(command_line, stdout=subprocess.PIPE).stdout.decode('utf-8')
    output.set_html(out)   

Gempyre.Element(ui, "run").subscribe('click', do_run)    
    
ui.run()


