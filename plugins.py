import os

plugins  = []
modified = {}
for item in open("plugin_list.txt", 'r'):
    plugin = item.strip('\n')

    try:
        m = __import__(plugin)
        plugins.append(m)
        lm = os.path.getmtime(plugin+".py")
        modified[plugin] = lm
    except ImportError:
        print "Plugin", plugin, "not found."
    except:
        print "Error in", plugin

def getResponse(msg):
    checkPlugins()

    resp = None
    for p in plugins:
        try:
            resp = p.computeResponse(msg)
            if not resp == None:
                break
        except:
            print "Plugin", p.__name__, "broke."

    if resp:
        return resp

def checkPlugins():
    for p in plugins:
        lm = os.path.getmtime(p.__name__+".py")
        if modified[p.__name__] != lm:
            try:
                reload(p)
            except:
                print p.__name__, "failed reloading"