import sys
import os
import Telex
from Telex_utils import resource

Telex.setDebug()
name = sys.argv[1]
map, names = resource.fromFile(name)
print(names[name], name)
ui = Telex.Ui(map, names[name])
ui.onUiExit(lambda: print("on Exit"))
ui.run()

