import os
import math

import xml.sax
import xml.etree.cElementTree as ET

with open("train.txt",'w') as f:
    pass
with open("trainval.txt",'w') as f:
    pass
with open("val.txt",'w') as f:
    pass
with open("test.txt",'w') as f:
    pass

first = os.getcwd()
try:
    os.chdir("theXML")
except:
    os.mkdir("theXML")
os.chdir(first)

class JetsonXMLHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.Databuff = ""

        self.FileName = ""
        theFolder = "FFBDataset"
        
        # Create xml structure
        self.XMLroot = ET.Element("annotation")

        ET.SubElement(self.XMLroot,"filename").text = "forfill.jpg"
        ET.SubElement(self.XMLroot,"folder").text = theFolder

        self.XMLsource = ET.SubElement(self.XMLroot,"source")

        ET.SubElement(self.XMLsource,"database").text = theFolder
        ET.SubElement(self.XMLsource,"annotation").text = "custom"
        ET.SubElement(self.XMLsource,"image").text = "custom"

        self.XMLsize = ET.SubElement(self.XMLroot,"size")

        ET.SubElement(self.XMLsize,"width").text = "1280"
        ET.SubElement(self.XMLsize,"height").text = "720"
        ET.SubElement(self.XMLsize,"depth").text = "3"

        ET.SubElement(self.XMLroot,"segmented").text = "0"
    
    def changeName(self,fileName):
        elm = self.XMLroot.find("filename")
        self.FileName= fileName
        elm.text = self.FileName
    
    def changeSize(self, Width, Height):
        elm = self.XMLsize.find("width")
        elm.text = Width
        elm = self.XMLsize.find("height")
        elm.text = Height

    def createObject(self, Label, bbox):
        self.XMLobject = ET.SubElement(self.XMLroot,"object")
   
        ET.SubElement(self.XMLobject,"name").text = Label
        ET.SubElement(self.XMLobject,"pose").text = "unspecified"
        ET.SubElement(self.XMLobject,"truncated").text = "0"
        ET.SubElement(self.XMLobject,"difficult").text = "0"
    
        self.XMLbndbox = ET.SubElement(self.XMLobject,"bndbox")
      
        ET.SubElement(self.XMLbndbox,"xmin").text = str(math.floor(bbox[0]))
        ET.SubElement(self.XMLbndbox,"ymin").text = str(math.floor(bbox[1]))
        ET.SubElement(self.XMLbndbox,"xmax").text = str(math.floor(bbox[2]))
        ET.SubElement(self.XMLbndbox,"ymax").text = str(math.floor(bbox[3]))
   
    def writeXML(self, which):
        tree = ET.ElementTree(self.XMLroot)
        deleted = self.FileName[0:-4]
        tree.write("./theXML/"+deleted+".xml")
        traintxt = open("train.txt",'a')
        trainvaltxt = open("trainval.txt",'a')
        valtxt = open("val.txt",'a')
        testtxt = open("test.txt",'a')
        if which.lower() == "train":
            traintxt.write(deleted+"\n")
            trainvaltxt.write(deleted+"\n")
        elif which.lower() == "val":
            valtxt.write(deleted+"\n")
            trainvaltxt.write(deleted+"\n")
        elif which.lower() == "test":
            testtxt.write(deleted+"\n")
        self.FileName = ""
        self.Databuff = ""

if __name__ == "__main__":
    jsonTOxml = JetsonXMLHandler()
    jsonTOxml.changeName("testing.jpg")
    for x in range(0,4):
        jsonTOxml.createObject('Accept', (x,1,350.0,350))
    jsonTOxml.writeXML('train')

