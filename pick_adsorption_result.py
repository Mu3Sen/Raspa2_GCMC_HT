#!/usr/bin/env python
import os
import re
import json

def iter_files(root_dir):
    outputfile = []
    for root,dirs,files in os.walk(root_dir):
        for file in files:
            file_name = os.path.join(root,file)
            outfile_extension = ".data"
            path,tmpfilename = os.path.split(file_name)
            filename,extension = os.path.splitext(tmpfilename)
            ads = str(file_name).split("/")[-5]
            if extension == outfile_extension and ads == "Adsorption":
                outputfile.append(file_name)

    return outputfile

def confirm_generate(filepath):
    generate = False
    calc_p_list = ["1e4", "1e5", "2e2", "2e4", "4e4", "5e3", "6e4", "8e4"]
    for i in calc_p_list:
        avp_path = filepath + os.sep + "Adsorption/" + i + os.sep + "Output/System_0/"
        result_path = filepath + os.sep + "Adsorption/" + i + os.sep + "Output"
        try:
            outfile = avp_path + "".join(os.listdir(avp_path))
        except FileNotFoundError:
            generate = False
        else:
            generate = True

    return generate

def check_exists_files(filepath):
    calc = False
    with open(filepath,"r") as f:
        data = f.read()
        #start_check = re.compile(r'Starting simulation')
        start_check = 'Starting simulation'
        #end_check = re.compile(r'Simulation finished,')
        end_check = 'Simulation finished,'
        #if ( start_check.findall(data) and end_check.findall(data) ) is not None:
        if end_check in data:
            calc = True
        else:
            calc = False

    return calc

def get_result(file):
    try:
        with open(file,"r") as resultf:
            info = resultf.read()
    #resultpat = re.compile(r"\s+[A]\w{6}\s\w{7}\s\w{8}\s[[].*?[]]\s+(-?\d+.\d+)\s[+]")
        resultpat = re.compile(r"\s+Average loading absolute [[]milligram/gram framework[]]\s+(-?\d+.\d+)")
        adsresult = resultpat.findall(info)
    #print(adsresult)
    except FileNotFoundError:
        pass  

    return adsresult

def return_data(mofpath):
    noncalc, nonf, result_list = [], [], []
    data = {}
    mofname = os.path.split(mofpath)[1]
    mofoutfile = iter_files(mofpath)
    mofoutfile.sort()
    generate = confirm_generate(mofpath)
    if generate:
        data.update(MOF_id = mofname)
        for outfile in mofoutfile:
            calc = check_exists_files(outfile)
            tmpoutfile_name = os.path.split(outfile)[1]
            outname = os.path.splitext(tmpoutfile_name)[0] 
            if calc:
                result = "".join(get_result(outfile))
                underp = str(outname).split("_")[-1]
                if len(result) != 0:
                    data[underp] = result
                else:
                    data[underp] = NotFound
            else:
                noncalc.append(mof)
                underp = str(outname).split("_")[-1]
                data[underp] = None
                #print("Calculation Not Finished  ", mof)
                with open("./nonf", "a+") as fnfile:
                    fnfile.writelines(mof + "\n")
    else:
        nonf.append(mof)
        #print("No Outfile found  ", mof)
        with open("./noncalc", "a+") as fncfile:
            fncfile.writelines(mof + "\n")

    return data

if __name__ == '__main__':
    import sys
    args = sys.argv
    mofdir = args[1]
    molecule = args[2]
    mof_result = os.listdir(mofdir)
    result_list = []
    for mof in mof_result:
        mofpath = mofdir + os.sep + mof
        data = return_data(mofpath)
        result_list.append(data)
    #jsondata = json.dumps(result_list)
    with open("/WORK/nscc-gz_material_1/MOFs/script/calc_result_data/result_Adsorption_" + molecule,"a+") as adsf:
        json.dump(result_list, adsf, sort_keys=False, indent=4, separators=(',', ': '))
