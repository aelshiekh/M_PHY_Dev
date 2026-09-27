#!/usr/bin/python3

import pandas as pd
import sys
import getopt
import os
from os import path

def open_tl_sheet(file_loc):
    # Updating the code to test Git Code Review Features
    df = pd.read_excel(file_loc, sheet_name=0)
    Module_name = df['ModuleName'].dropna().tolist()
    TL_Pins     = df['Pin'].dropna().tolist()
    TL_Dir      = df['Direction'].dropna().tolist()
    TL_Width    = df['Width'].dropna().tolist()
    
    if(len(TL_Dir) == len(TL_Pins) == len(TL_Width)):
        pass
    else:
        print("Error: Missing Parameters - Please check your excel sheet")
        sys.exit(1)
    
    return Module_name,TL_Pins,TL_Dir,TL_Width

def print_verilog_tl(module_name,pin_name,pin_dir,pin_width):
    file_name = "../TL_Wrapper/%s.v" % module_name
    with open (file_name,"a") as f:
    # Printing with + eliminates auto-space between word, while , creates auto-space
        f.write("module " + module_name + " ("+','.join(pin_name)+");\n\n")
        for (pin,direction,width) in zip(pin_name,pin_dir,pin_width):
            if((width==1.0) & (direction == "IN")):
                f.write("input  %s;\n" %(pin))
            elif ((width!=1.0) & (direction == "IN")):
                f.write("input  [%d:0] %s;\n" %(width-1,pin))
            elif ((width==1.0) & (direction == "OUT")):
                f.write("output %s;\n" %(pin))
            elif ((width!=1.0) & (direction == "OUT")):
                f.write("output [%d:0] %s;\n" %(width-1,pin))
        f.write("\n")

def get_hier(file_loc,num):
    
    df = pd.read_excel(file_loc, sheet_name=num)
    Module_name = df['ModuleName'].dropna().tolist()
    TL_Pins     = df['Pin'].dropna().tolist()
    TL_Dir      = df['Direction'].dropna().tolist()
    TL_Width    = df['Width'].dropna().tolist()
    TL_Conn     = df['Connection'].dropna().tolist()
    
    if(len(TL_Dir) == len(TL_Pins) == len(TL_Width) == len(TL_Conn)):
        pass
    else:
        print("Error: Missing Parameters - Please check your excel sheet")
        sys.exit(1)
    
    return Module_name,TL_Pins,TL_Dir,TL_Width,TL_Conn

def prepare_working_area():
    if(path.exists("../TL_Wrapper")):
        if(path.exists("../TL_Wrapper/dwc_mphy_tx_4l.v")):
            os.remove("../TL_Wrapper/dwc_mphy_tx_4l.v")
    else:
        os.mkdir("../TL_Wrapper")

def get_modules_list(file_loc):
    
    all_modules = pd.ExcelFile(file_loc).sheet_names
    all_modules = all_modules[1:]
    return all_modules

def print_verilog_hier(wrapper_file,instance_name,module_name,Pins,Conn):
    conn_count = len(Pins)
    i = 1
    file_name = "../TL_Wrapper/%s.v" % wrapper_file
    with open (file_name,"a") as f:
        f.write("\n" + instance_name + " " + module_name + " (\n")
        for (pin,conn) in zip(Pins,Conn):
            if(conn_count == i):
                f.write("."+pin+"("+conn+")"+"\n);\n\n")
            else:
                f.write("."+pin+"("+conn+"),\n")
            i = i+1

def create_wires(wrapper_file,TL_Pins,Width,Conn):
    file_name = "../TL_Wrapper/%s.v" % wrapper_file
    with open (file_name,"r+") as f:
        loglist = f.readlines()
        for (width,conn) in zip(Width,Conn):
            if(conn in TL_Pins):
                pass
            elif(width==1):
                line = "wire %s;\n" %(conn)
                if (line in loglist):
                    pass
                else:
                    f.write("wire %s;\n" %(conn))
            else:
                line = "wire [%d:0] %s;\n" %(width-1,conn)
                if (line in loglist):
                    pass
                else:
                    f.write("wire [%d:0] %s;\n" %(width-1,conn))

def print_eof(wrapper_file):
    file_name = "../TL_Wrapper/%s.v" % wrapper_file
    with open (file_name,"a") as f:
        f.write("\nendmodule")

def generate_wrapper():
    prepare_working_area()
    TL_Excel_Sheet = "../TL_Sheet/toplevel.xlsx"
    var = open_tl_sheet(TL_Excel_Sheet)
    tl_name = ''.join(var[0])
    print_verilog_tl(tl_name,var[1],var[2],var[3])
    all_modules=get_modules_list(TL_Excel_Sheet)
    for i in range(len(all_modules)):
        hier=get_hier(TL_Excel_Sheet,i+1)
        create_wires(tl_name,var[1],hier[3],hier[4])
    for i in range(len(all_modules)):
        hier=get_hier(TL_Excel_Sheet,i+1)
        sub_module = all_modules[i]
        inst_name = ''.join(hier[0])
        print_verilog_hier(tl_name,inst_name,sub_module,hier[1],hier[4])
    print_eof(tl_name)

def excel2csv(file_loc):
    if(path.exists("../CSVs")):
        pass
    else:
        os.mkdir("../CSVs")
    df = pd.read_excel(file_loc, sheet_name=None)
    for key in df.keys():
        df[key].to_csv('../CSVs/%s.csv' %key,index=False)

def csv2excel():
    writer = pd.ExcelWriter('../TL_Sheet/toplevel.xlsx')
    CSVs = os.listdir("../CSVs")
    csv_dir  = "../CSVs/"
    CSVs_dir = [csv_dir + s for s in CSVs]
    for csvfilename,csvfiledir in zip(CSVs,CSVs_dir):
        df = pd.read_csv(csvfiledir)
        df.to_excel(writer,sheet_name=os.path.splitext(csvfilename)[0],index=False)
        writer.save()

def user_manual():
    print("Script Help")
    print ("\ttop_level.py -c - Used to generate CSV from Excel Sheet")
    print ("\ttop_level.py -c - Used to generate Excel Sheet from CSV")
    print ("\ttop_level.py -w - Used to generate Top Level Wrapper")
    sys.exit(2)

def main(argv):
    code_func = ""
    if (len(sys.argv) == 1):
        print("No Arguments Passed - Exiting")
        user_manual()
    elif (len(sys.argv) > 3):
        print("Extra Arguments Passed - Exiting")
        user_manual()
    try:
        opts, args = getopt.getopt(argv,"hf:",["function="])
    except getopt.GetoptError:
        print("Incorrect Parameters Passed - Exiting")
        user_manual()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            user_manual()
            sys.exit()
        elif opt in ("-f", "--function"):
            code_func = arg
            if (code_func == "wrapper"):
                generate_wrapper()
                print("Top Level Wrapper Generated")
            elif (code_func == "csv2excel"):
                csv2excel()
                print("Excel Sheet Generated")
            elif (code_func == "excel2csv"):
                excel2csv("../TL_Sheet/toplevel.xlsx")
                print("CSV Files Generated")

if __name__ == "__main__":
    main(sys.argv[1:])
