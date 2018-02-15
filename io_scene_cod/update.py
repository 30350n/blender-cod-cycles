from io_scene_cod.__init__ import bl_info
import requests

def getVersion():
    s = requests.Session()
    version = None
    
    try:
        version = [int(i) for i in s.post("http://codmvm.com/iw3d/iw3d_version.php", headers={"plugin" : "BLENDER-COD-CYCLES"}, timeout=2).content.decode().split(":")]
    
    except:
        version = None
    
    s.close()
    return version

def printVersion(version, url=False):
    result = ""
    for i in version:
        result += str(i) + ("_" if url else ".")

    return result[:-1]

def isUpToDate(ver1, ver2):
    n = 0
    while n < len(ver1) and n < len(ver2):
        if ver1[n] != ver2[n]:
            return ver1[n] > ver2[n]
        n += 1

    return len(ver1) >= len(ver2)

version = bl_info["version"]
serverVersion = getVersion()

if serverVersion:
    if not isUpToDate(version, serverVersion):
        import ctypes, webbrowser
        if 1 == ctypes.windll.user32.MessageBoxW(None, "A newer version is available! (%s)\nClick 'OK' to download it!\n\nRemove the old plugin, restart Blender, then install the new plugin and enable it!" % printVersion(serverVersion), "BLENDER-COD-CYCLES Updater", 1):
            webbrowser.open("https://codmvm.com/downloads/iw3d/blendercodcycles.php")
