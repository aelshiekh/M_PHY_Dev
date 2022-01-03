#!/usr/bin/python3

import pandas as pd
import sys
import os
from os import path

def open_tl_sheet(file_loc):
    
    df = pd.read_excel(file_loc, sheet_name=0)
    TL_Pins  = df['Pin'].dropna().tolist()
    TL_Dir   = df['Direction'].dropna().tolist()
    TL_Width = df['Width'].dropna().tolist()
    
    if(len(TL_Dir) == len(TL_Pins) == len(TL_Width)):
        print("All Parameters Extracted Successfully")
    else:
        print("Error: Missing Parameters - Please check your excel sheet")
        sys.exit(1)
    
    return TL_Pins,TL_Dir,TL_Width

def print_verilog(pin_name,pin_dir,pin_width):
    with open ("../TL_Wrapper/toplevel.v","a") as f:
    # Printing with + eliminates auto-space between word, while , creates auto-space
        f.write("module top_level("+','.join(pin_name)+");\n\n")
        for (pin,direction,width) in zip(pin_name,pin_dir,pin_width):
            if((width==1.0) & (direction == "IN")):
                f.write("input %s;\n" %(pin))
            elif ((width!=1.0) & (direction == "IN")):
                f.write("input [%d:0] %s;\n" %(width-1,pin))
            elif ((width==1.0) & (direction == "OUT")):
                f.write("output %s;\n" %(pin))
            elif ((width!=1.0) & (direction == "OUT")):
                f.write("output [%d:0] %s;\n" %(width-1,pin))
        f.write("\nendmodule")

def prepare_working_area():
    if(path.exists("../TL_Wrapper")):
        if(path.exists("../TL_Wrapper/toplevel.v")):
            os.remove("../TL_Wrapper/toplevel.v")
    else:
        os.mkdir("../TL_Wrapper")

prepare_working_area()
var = open_tl_sheet("../TL_Sheet/toplevel.xlsx")
print_verilog(var[0],var[1],var[2])
