#!/usr/bin/env python 
import subprocess
import os
        

directory = '../run_once'

files_which_already_ran_fn = directory+"/files_which_already_ran.txt"
if os.path.isfile(files_which_already_ran_fn):
    with open(files_which_already_ran_fn, 'r') as files_which_already_ran_file:
        
        files_which_already_ran = [line.strip() for line in files_which_already_ran_file.readlines()]
else:
    files_which_already_ran = []
    
print(files_which_already_ran)

files_i_run = []

files_to_run = []

for filename in os.listdir(directory):
    if filename.endswith(".sh") or filename.endswith(".py"):

        full_path = os.path.join(directory, filename)
        isexecutable = os.access(full_path, os.X_OK)
        if isexecutable:
            files_to_run.append(full_path)

files_to_run.sort()
for full_path in files_to_run:
    if full_path in files_which_already_ran:
        print("Skipping: "+full_path)
        continue

    print("Running: "+full_path)
    stdoutput = subprocess.Popen(full_path, shell=True,stdout=subprocess.PIPE).stdout.read()
    print(stdoutput)
    files_which_already_ran.append(full_path)

print(files_which_already_ran)

with open(files_which_already_ran_fn, 'w') as files_which_already_ran_file:
    for file_name_to_not_run_again in files_which_already_ran:
        files_which_already_ran_file.write("%s\n" % file_name_to_not_run_again)
