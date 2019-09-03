#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import shutil
import mofs_calc_dir

''' 

Extract Helium void Fraction from before calculation and perform Adsorption calculation
: CIFPATH + INDIVIDUAL CIF DIRECTORY
eg: python MOFs_step2.py /WORK/nscc-gz_material_5/MOF/test/ref_try/mofdb/cif/ABAFUH.MOF_subset

'''

def read_output(filepath):
    output_file_path = filepath +"/HeliumVF/Output/System_0/"
    mof_cif_name = filepath.split(os.sep)[-1]
    try:
        ofn = os.listdir(output_file_path)
        output_file = output_file_path+"".join(ofn)
    #print(output_file)
        pat = "Rosenbluth factor new: (\d+.\d+)"
        hvf_value = re.findall(pat,open(output_file).read())[-1]
    #print(hvf_value)
    except FileNotFoundError:
        print(mof_cif_name," no hvf value,skipping")  
        with open("/WORK/nscc-gz_material_1/MOFs/script/adsorption_without_hvf.txt","a+") as f:
            f.writelines(mof_cif_name)
        hvf_value = None

    return hvf_value

def modify_input(filepath):
    hvf_value = read_output(filepath)
    pat = "hvf_value"
    ads_path = filepath + "/Adsorption"
    modify_file = ads_path + "/simulation.input"
    new_simulation = filepath + "/Adsorption/newsimulation.input"
    open(new_simulation, 'w').write(re.sub(pat, str(hvf_value), open(modify_file).read()))
    os.system('mv '+ new_simulation + ' ' + modify_file)

    return ads_path

def apply_pressure(filepath,mode,part):
    pressure = ["2e2","5e3","1e4","2e4","4e4","6e4","8e4","1e5"]
    diff_p_path = modify_input(filepath)
    pat = "pressure_value"
    #print(diff_p_path)
    files = os.listdir(diff_p_path)
    homepath = os.path.expanduser('~')
    adsorption_joblist_path = homepath + "/MOFs/work/"+ mode + "_" + part+"/MOF_ADS/Joblist/Adsorption"
    for p in pressure:
        p_path = diff_p_path + os.sep + p + os.sep
        os.mkdir(p_path)
        for i in files:
            shutil.copyfile(diff_p_path + os.sep + i, p_path + i)
        old_input_file = p_path + "/simulation.input"
        new_input_file = p_path + "/ap_simulation.input"
        cifname = mofs_calc_dir.find_cif(p_path)
#P
        open(new_input_file, 'w').write(re.sub(pat, p, open(old_input_file).read()))
        os.system('mv ' + new_input_file + ' ' + old_input_file)
        #homepath = os.path.expanduser('~')
        #adsorption_joblist_path = homepath + "/MOF_WORK/Joblist/Adsorption/"
        if not os.path.exists(adsorption_joblist_path):
            os.makedirs(adsorption_joblist_path)
        submit2_sh = ["#!/bin/sh\n",
                      "cd "+ p_path +"\n", 
                      "export RASPA_DIR=/WORK/nscc-gz_material_1/MOFs/sf_box/raspa2/src\n",
                      "$RASPA_DIR/bin/simulate\n"
                     ]
        os.chdir(adsorption_joblist_path)
        sub_file = "ads" + "".join(cifname) +"_"+ p + ".sh"
        with open(r"./" + sub_file, "w") as f_sub:
            f_sub.writelines(submit2_sh)

    return adsorption_joblist_path

if __name__ == '__main__':
    import sys
    args = sys.argv
    filepath = args[1]
    mode = args[2]
    part = args[3]
    apply_pressure(filepath,mode,part)
