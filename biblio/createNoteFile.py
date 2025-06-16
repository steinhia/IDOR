# coding: utf-8
import os
import sys
from os import path
import glob

def create(name):
    if not(os.path.exists(name)):
        f=open(name,"w")
        f.write("PasLu \n \n")
        f.write("## Resume \n \n")
        f.write("## Introduction \n \n")
        f.write("## Etude \n \n")
        f.write("## Discussion \n \n")
        f.close()



if len(sys.argv)>1:
    name="notesBiblio/"+sys.argv[1]
    create(name)
else:
    for filename in glob.glob(os.path.join("PDF", '*.pdf')):
        name="notesBiblio/"+os.path.basename(filename).replace("pdf",'md')
        create(name)
