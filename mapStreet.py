import os
import lxml.etree as ET

fp = "maps"
op = "mapStreet"

for root,dirs,files in os.walk(fp):
    for file in files:
        fcur = fp+'\\'+file

        myMap = ET.parse(fcur)

        root = myMap.getroot()

        delset = set()
        keepset = set()

        for child in root:
            keep = 0
            
            for tag in child:
                if (tag.get('k') == 'highway'): 
                    if ((tag.get('v') == 'motorway') or (tag.get('v') == 'trunk') or (tag.get('v') == 'primary') or (tag.get('v') == 'secondary') or (tag.get('v') == 'tertiary')):
                        keep = 1
                    
                    
            if (keep == 1): 
                ats = child.attrib
                keepset.add(ats.get("id"))
                
                for tag in child:
                    if(tag.get("ref") != None):
                        keepset.add(tag.get("ref"))

        for child in root: 
            ats = child.attrib
            id = ats.get("id")
            
            if (not(id in keepset)):
                try:
                    root.remove(child)
                except ValueError:
                    pass
                
        myMap.write(op+'\\'+file)
