#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import math
import shutil
import readcif

''' 
Create an initial calculation folder and all simulation input file templates
(Helium void Fraction; Adsorption; Henry coefficient;) and calculate the unitcell value;
CIFPATH 
eg: python MOFs_step1.py /WORK/nscc-gz_material_5/MOF/test/ref_try/mofdb/cif
'''

def find_cif(filepath):
    f_list = os.listdir(filepath)
    cifs = [os.path.splitext(i)[0] for i in f_list if os.path.splitext(i)[1] == '.cif']

    return cifs

def calc_directory(filepath):
    cifs = find_cif(filepath)
    mof_file_dir = []
    for mof_name in cifs:
        src_file = filepath + os.sep + mof_name + ".cif"
        des_path = filepath + os.sep + mof_name + os.sep
        des_file = des_path + mof_name + ".cif"
        os.chdir(filepath)
        if not os.path.exists(des_path):
            os.mkdir(des_path)
        shutil.move(src_file,des_file)
        mof_file_dir.append(des_path)

    return mof_file_dir

def babel_cif(cifname):
    mof_file = cifname
    calc_cif = mof_file
    #babel_mof_file = "babel_" + mof_file
    #babelcmd = "babel " + mof_file + " " + babel_mof_file
    
    try:
        os.system(babelcmd)
        os.remove(cifname)
        calc_cif = babel_mof_file
    except:
        print("babel conversion error!")
        calc_cif = mof_file
        with open("~/MOFslog","a+") as bb_error:
            bb_error.writelines(cifname+"\n")
    
    return calc_cif

def unitcell_value(filename):
    cif_data = readcif.read_cif_file(filename)
    lattice = readcif.get_lattice(cif_data)
    a, b, c = lattice[0], lattice[1], lattice[2]
    av, bv, cv = 0, 0, 0
    for i in range(3):
        av += a[i] ** 2
        bv += b[i] ** 2
        cv += c[i] ** 2
    av, bv, cv = math.sqrt(av), math.sqrt(bv), math.sqrt(cv)
    # print(av,bv,cv)
    ra, rb, rc = 26 / av, 26 / bv, 26 / cv
    l = [ra, rb, rc]
    # print(l)
    for num in range(3):
        if abs(l[num] - round(l[num])) < 0.5:
            l[num] += 1
        la, lb, lc = int(l[0]), int(l[1]), int(l[2])
    length = str(la) + " " + str(lb) + " " + str(lc)

    return length

def calc_propery(filepath,mode,part):
    os.chdir(filepath)
    calc_list = ["HeliumVF","Adsorption","HenryC"]
    homepath = os.path.expanduser('~')
    if mode == "hvf":
        path == calc_list[0]
        joblist_path = homepath + "/MOFs/work/"+ mode + "_" + part+"/MOF_VF/Joblist/VoidFraction"
        if not os.path.exists(joblist_path):
            os.makedirs(joblist_path)
    elif mode == "ads":
        path == calc_list[1]
        joblist_path = homepath + "/MOFs/work/"+ mode + "_" + part+"/MOF_ADS/Joblist/Adsorption"
        if not os.path.exists(joblist_path):
            os.makedirs(joblist_path)
    elif mode == "hc":
        path == calc_list[2]
        joblist_path = homepath + "/MOFs/work/"+ mode + "_" + part+"/MOF_HC/Joblist/HenryC"
        if not os.path.exists(joblist_path):
            os.makedirs(joblist_path)
    #heliumvf_job_path_list,henryc_job_path_list = [],[]
    
    os.mkdir(filepath + os.sep + path)
    filename = "".join(find_cif(filepath))
    cif_file = "".join(filename)+".cif"
    des_path = filepath + path + os.sep
    src_file = filepath + cif_file
    des_file = des_path + cif_file
    shutil.copyfile(src_file, des_file)
    os.chdir(des_path)
    length = unitcell_value(cif_file)
    submit1_sh = ["#!/bin/sh\n",
                  "cd "+des_path+"\n", 
                  "export RASPA_DIR=/WORK/nscc-gz_material_1/MOFs/sf_box/raspa2/src\n",
                  "$RASPA_DIR/bin/simulate\n"
                 ]
    if mode == "hvf":  
        s_hvf_in = ["SimulationType        MonteCarlo\n",
                    "NumberOfCycles        10000\n",
                    "PrintEvery            1000\n",
                    "PrintPropertiesEvery  1000\n",
                    "\n",
                    "Forcefield            UFF4MOFs\n",
                    "\n",
                    "Framework 0\n",
                    "FrameworkName" + "     " + str(filename) + "\n",
                    "UnitCells" + "         " + length + "\n",
                    "ExternalTemperature 298.0\n",
                    "\n",
                    "Component 0  MoleculeName             " + "helium" + "\n",
                    "             MoleculeDefinition       TraPPE\n",
                    "             WidomProbability         1.0\n",
                    "             CreateNumberOfMolecules  0\n"
                    ]

        sub_file = "hvf" + str(filename) + ".sh"
        with open("./simulation.input", "w") as f_hvf:
            f_hvf.writelines(s_hvf_in)
        os.chdir(joblist_path)
        with open(r"./" + sub_file, "w") as f_sub:
            f_sub.writelines(submit1_sh)
            
    elif mode == "ads":
        s_adp_in = ["SimulationType        MonteCarlo\n",
                    "NumberOfCycles        10000\n",
                    "NumberOfInitializationCycles 5000\n"
                    "PrintEvery            1000\n",
                    "PrintPropertiesEvery  1000\n",
                    "\n",
                    "Forcefield            UFF4MOFs\n",
                    "ChargeFromChargeEquilibration yes\n",
                    "CutOff                12.8\n",
                    "\n",
                    "Framework 0\n",
                    "FrameworkName" + "     " + str(filename) + "\n",
                    "UnitCells" + "         " + length + "\n",
                    "ExternalTemperature 77.0\n",
                    "HeliumVoidFraction" + "  hvf_value" + "\n",
                    "ExternalPressure   pressure_value\n",
    
                    "\n",
                    "Component 0  MoleculeName             N2\n",
                    "             TranslationProbability   0.5\n",
                    "             RotationProbability      0.5\n",
                    "             ReinsertionProbability   0.5\n",
                    "             SwapProbability          1.0\n",
                    "             CreateNumberOfMolecules  0\n"
                    ]
        #sub_file = "ads" + str(filename) + ".sh"
        with open("./simulation.input", "w") as f_ads:
            f_ads.writelines(s_adp_in)
        #os.chdir(adsorption_joblist_path)
        #with open(r"./" + sub_file, "w") as f_sub:
        #    f_sub.writelines(submit_sh)
       
    elif mode == "hc":
        s_hc_in = ["SimulationType        MonteCarlo\n",
                   "NumberOfCycles        10000\n",
                   "NumberOfInitializationCycles 0\n"
                   "PrintEvery            1000\n",
                   "PrintPropertiesEvery  1000\n",
                   "\n",
                   "Forcefield            UFF4MOFs\n",
                   "\n",
                   "Framework 0\n",
                   "FrameworkName" + "     " + str(filename) + "\n",
                   "RemoveAtomNumberCodeFromLabel  yes\n"
                   "UnitCells" + "         " + length + "\n",
                   "ExternalTemperature 77.0\n",
                   "\n",
                   "Component 0  MoleculeName             N2\n",
                   "             MoleculeDefinition       TraPPE\n",
                   "             IdealRosenbluthValue     1.0\n",
                   "             WidomProbability         1.0\n",
                   "             CreateNumberOfMolecules  0\n"
                   ]
        sub_file = "hc" + str(filename) + ".sh"
        with open("./simulation.input", "w") as f_ads:
            f_ads.writelines(s_hc_in)
        os.chdir(joblist_path)
        with open(r"./" + sub_file, "w") as f_sub:
            f_sub.writelines(submit1_sh)
        
        return joblist_path

if __name__ == '__main__':
    import sys
    args = sys.argv
    filepath = args[1]
    mode = args[2]
    part = args[3]
    work_dir = calc_directory(filepath)
    for mofpath in work_dir:
        filename = find_cif(mofpath)
        #print(filename)  
        os.chdir(mofpath)
        calc_cif = babel_cif("".join(filename)+".cif")
        #print(calc_cif)
        calc_propery(mofpath,mode,part)