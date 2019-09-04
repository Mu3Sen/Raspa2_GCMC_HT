#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import random
import string
import mofs_calc_dir

'''
Create batch job submission script path and script file;
eg: python *.py ~/MOF_WORK/Joblist/HeliumVF
'''

def creat_workdir(homepath,mode,part):
    submit_workdir = homepath + "/MOFs/work/MOF_WORK/"+ mode+"_"+ part+"/Submit_sh/"
    if not os.path.exists(submit_workdir):
        os.makedirs(submit_workdir)
    if mode == "hvf":
        sh_path = homepath +  "/MOFs/work/MOF_VoidFraction/"+ mode + "_" + part +"/Joblist/VF/"
        if not os.path.exists(sh_path):
            os.makedirs(sh_path)
    elif mode == "ads":
        sh_path = homepath + "/MOFs/work/MOF_Adsorption/"+ mode + "_" + part +"/Joblist/ADS/"
        if not os.path.exists(sh_path):
            os.makedirs(sh_path)
    elif mode == "hc":
        sh_path = homepath + "/MOFs/work/MOF_HenryC/"+ mode + "_" + part +"/Joblist/HC/"
        if not os.path.exists(sh_path):
            os.makedirs(sh_path)

    return sh_path,submit_workdir

def split_job(mode,shpath,part):
    homepath = os.path.expanduser('~')
    shnum = 24
    batchdir = creat_workdir(homepath,mode,part)[0]
    #print(batchdir)
    filepath = shpath
    #print(filepath)
    total_sh = os.listdir(filepath)
    #print(total_sh)
    total_num = len(total_sh)
    #print(total_num)
    batch_name = [total_sh[i:i + shnum] for i in range(0, total_num, shnum)]
    batchnum = len(batch_name)
    batchlist =[]
    #print(batchnum)
    for run_i in range(batchnum):
        id_num = random.randint(0,50000)
        id_str = string.ascii_lowercase 
        r_str = random.choice(id_str)
        codename = "run_mof"+str(r_str)+str(id_num)+"_"+ str(run_i) + ".sh"
        batchlist.append(batchdir + codename)
        with open(batchdir + os.sep + codename, "w") as fm:
            fm.writelines("#!/bin/bash\n")
            for item in batch_name[run_i]:
                #print(item)
                if item in batch_name[run_i][0:-1]:
                    fm.writelines("bash " + filepath +os.sep + item + "  &\n")
                if item == batch_name[run_i][-1]:
                    #print("This is the last", item)
                    fm.writelines("bash " + filepath +os.sep+ item + "  &\nwait")
    return batchlist

def submit_job(mode,shpath,part):
    homepath = os.path.expanduser('~')
    submit_path = creat_workdir(homepath,mode,part)[1]
    #print(submit_path)
    if mode == "hvf":
        submit_dir = submit_path + "/hvf_submit"
        if not os.path.exists(submit_dir):
            os.makedirs(submit_dir)
    elif mode == "ads":
        submit_dir = submit_path + "/ads_submit"
        if not os.path.exists(submit_dir):
            os.makedirs(submit_dir)
    elif mode == "hc":
        submit_dir = submit_path + "/hc_submit"
        if not os.path.exists(submit_dir):
            os.makedirs(submit_dir)
    batch_list = split_job(mode,shpath,part)
    os.chdir(submit_dir)
    yhbatch_id = []
    job_total = len(batch_list)
    counter = 0
    for batch in batch_list:
        batchname = "".join(batch)
        os.system("yhbatch -N 1 " + batchname)
        job_num_cmd = "squeue | wc | awk \'{print $1}\'"
        job_num = int("".join(os.popen(job_num_cmd).readlines())) - 1
        batchcmd = batchname.split(os.sep)[-1]
        id_cmd = "yhacct  --name  " + batchcmd + " | awk '{print $1;}' | sed -n \"3, 1p\""
        time.sleep(3)
        job_id = "".join(os.popen(id_cmd).readlines())
        yhbatch_id.append(job_id)
        time.sleep(3)
        while job_num > 300: # Node limit(i): can submit i+1 job
            print("Reach Node limit...waiting")
            job_num = int("".join(os.popen(job_num_cmd).readlines())) - 1
            time.sleep(10)
        while check_job(batchcmd) is not True:
            print("check if this "+job_id+"job is submitted...")
            time.sleep(5)
        job_total -= 1
        counter +=1
        print(str(job_id)+" Successfully submitted, remain "+str(job_total))
        with open("./sucesscalc.txt","a+") as f_work:
            f_work.writelines(batchname+"  "+ str(counter) +"\n")
        submission = False
        if job_total == 0:
            print("Job submission completed!")
            submission = True

    return submission

def check_job(batchname):
    id_cmd = "yhacct  --name  " + batchname.replace("\n","") +"  "+"| awk '{print $1;}' | sed -n \"3, 1p\""
    #print("id_cmd is\n ",id_cmd)
    job_id = "".join(os.popen(id_cmd)).replace("\n","")
    state_cmd = "yhacct  -j  "+job_id.replace("\n","")+"| awk '{print $6;}'| sed -n \"3, 1p\""
    #print("state_cmd is \n ",state_cmd)
    job_state = "".join(os.popen(state_cmd)).replace("\n","")
    #print(job_id)
    #print(job_state)
    if job_state == "RUNNING":
        slurm = True
    elif job_state == "COMPLETED":
        with open("./Named_duplicate.txt","a+") as f1:
            f1.writelines(batchname+"\n")
        slurm = True
    elif job_state == "CANCELLED+":
        with open("./Submit_failed.txt","a+") as f2:
            f2.writelines(batchname+"\n")
        slurm = True
    else:
        slurm = False

    return slurm

def check_finished_job(batch_id):
    state_cmd = "yhacct  -j  "+ batch_id.replace("\n","") +"| awk '{print $6;}'| sed -n \"3, 1p\""
    job_state = "".join(os.popen(state_cmd)).replace("\n","")
    if job_state == "COMPLETED":
        slurm = True
    else:
        slurm = False

    return slurm

if __name__ == '__main__':
    import sys
    args = sys.argv
    filepath = args[1]
    mode = args[2]
    part = args[3]
    homepath = os.path.expanduser('~')
    creat_workdir(homepath,mode,part)
    #split_job(mode,filepath)
    submit_job(mode,filepath)
