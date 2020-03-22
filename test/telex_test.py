import sys
import os
import Telex
from datetime import datetime
from datetime import date
from datetime import timedelta
from Telex_utils import resource

#Telex.setDebug()
name = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(sys.argv[0]), "python_test_1.html")
map, names = resource.fromFile(name)
print(names[name], name)

ui = Telex.Ui(map, names[name])

ver, major, minor = Telex.version()
Telex.Element(ui, 'ver').setHTML("Telex Version: " + str(ver) + '.' + str(major) + '.' + str(minor));

def onStart():
    print(ui.root().html())

ui.onOpen(onStart)

ui.startTimer(timedelta(seconds=1), False, lambda: Telex.Element(ui, 'time').setHTML(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

elementCount = 0

addbutton = Telex.Element(ui, 'do')
def addElement(event):
    global elementCount
    new = Telex.Element(ui, "name_" + str(elementCount), "img", ui.root())
    elementCount += 1
    new.setAttribute("SRC", "https://www.animatedimages.org/data/media/202/animated-dog-image-0931.gif")

    

addbutton.subscribe('click', addElement)

removebutton = Telex.Element(ui, 'take')

def removeElement(event):
    global elementCount
    if elementCount <= 0:
        return
    elementCount -= 1
    Telex.Element(ui, "name_" + str(elementCount)).remove()
removebutton.subscribe('click', removeElement)

ui.onExit(lambda: print("on Exit"))
ui.run()

