import sys
import copy
import csv
import argparse
import os


#data structures

#This list will hold all policies as list elements.
#Elements of this be based on 'policy' data strcuture (disctionary)
policies_set=[]

#need header for CSV export
policy_description=['VSYS','from-zone','to-zone',"policy-name", 'source-address','destination-address','application','source-identity',"global-from-zone","global-to-zone","action"]

#Main data strcutre describing policy
policy = {
"VSYS": "GLOBAL",
"from-zone": "",
"to-zone": "",
"policy-name": "",
"source-address": [],
"destination-address": [],
"application": [],
"source-identity": [],
"global-from-zone": [],
"global-to-zone": [],
"action": []
}


# Functions

#This function checks whether there is existing policy in the list
#if policy is found then it returns index (int) value - reference point to position on the list
#if not found return -1 as 0 points to 0 position in the list so it would point something
def find_policy(l_vsys, l_from_zone, l_to_zone, l_policy_name):
    if not policies_set:
        return -1
    index=0
    for policy in policies_set:
        if policy["VSYS"]==l_vsys and policy["from-zone"]==l_from_zone and policy["to-zone"]==l_to_zone and policy["policy-name"]==l_policy_name:
            return index
        else:
            index=index+1
    return -1


#main script

parser = argparse.ArgumentParser(prog='juniper-policy-parser',description='Script takes 1 argument of a config file (typically .conf) and outputs CSV file with ".csv" extension with the same name as orginal file.',epilog='by Lukasz Awsiukiewicz, biuro@la-tech.pl')
parser.add_argument('-f', '--file', help='%(prog)s --filein=<juniper conf file in set format>')
a1 = parser.parse_args()

f_in_name=vars(a1)["file"]
if not(os.path.exists(f_in_name)):
    print("file not found!")
    exit()
f_out_name=f_in_name + ".csv"

with open(f_in_name, "r", encoding="utf8") as f:
    for line in f.readlines():
        #filter out configuration file based on 3 filter settings:
        #1. set security policies from-zone
        #2. set logical-systems <name> security policies global
        #3. set security policies global

        # I leave set security polices at the end for processing as its easier to filer based on just security policies from-zone
        #that returns policies from main virtual system and from defined virtual systems
        #by using if's i'm chosing format that I will work with

        if 'security policies from-zone' in line:
            #first lets handle policies from global/main virtual system
            if 'set security policies from-zone' in line:
                #grabing a line and spliting based on ' '
                data=line.split()
                from_zone=data[4]
                to_zone=data[6]
                policy_name=data[8]
                policy_property=data[9]
                #checking what is the term in the policy as after it, there is different data strcuturte
                if policy_property=='match':
                    property_type=data[10]
                    propery_value=data[11]
                    #trying to find on the list if this policy already exist
                    policy_index=find_policy("GLOBAL", from_zone, to_zone, policy_name)
                    #if not found then:
                    if policy_index==-1:
                        #create a full new variable with its own memory location and address
                        temp_policy=copy.deepcopy(policy)
                        temp_policy["from-zone"]=from_zone
                        temp_policy["to-zone"]=to_zone
                        temp_policy["policy-name"]=policy_name
                        temp_policy[property_type].append(propery_value)
                        #add to policies_set
                        policies_set.append(temp_policy)
                    #if yes - found
                    else:
                        #grab pointer from existing policy
                        temp_policy=policies_set[policy_index]
                        #add information.
                        temp_policy[property_type].append(propery_value)
                        #update existing policy
                        policies_set[policy_index]=temp_policy

                elif policy_property=='then':
                    policy_index=find_policy("GLOBAL", from_zone, to_zone, policy_name)
                    propery_value=data[10]
                    temp_policy=policies_set[policy_index]
                    temp_policy["action"].append(propery_value)
                    #print(from_zone, to_zone, policy_name, property_type, propery_value)
            #then let's handle policies from specific virtual system
            elif 'set logical-systems' in line:
                #parameters to be covered:
                #set logical-systems <name> security policies

                data=line.split()
                vsys=data[2]
                from_zone=data[6]
                to_zone=data[8]
                policy_name=data[10]
                policy_property=data[11]
                if policy_property=='match':
                    property_type=data[12]
                    propery_value=data[13]
                    policy_index=find_policy(vsys, from_zone, to_zone, policy_name)
                    if policy_index==-1:
                        temp_policy=copy.deepcopy(policy)
                        temp_policy["VSYS"]=vsys
                        temp_policy["from-zone"]=from_zone
                        temp_policy["to-zone"]=to_zone
                        temp_policy["policy-name"]=policy_name
                        temp_policy[property_type].append(propery_value)
                        policies_set.append(temp_policy)
                    else:
                        temp_policy=policies_set[policy_index]
                        temp_policy[property_type].append(propery_value)
                        policies_set[policy_index]=temp_policy

                elif policy_property=='then':
                    policy_index=find_policy(vsys, from_zone, to_zone, policy_name)
                    propery_value=data[12]
                    temp_policy=policies_set[policy_index]
                    temp_policy["action"].append(propery_value)
                    #print(from_zone, to_zone, policy_name, property_type, propery_value)
        elif 'set security policies global' in line:
            #set security policies global
            data=line.split()
            vsys="GLOBAL"
            from_zone="GLOBAL"
            to_zone="GLOBAL"
            policy_name=data[5]
            policy_property=data[6]
            if policy_property=='match':
                property_type=data[7]
                propery_value=data[8]
                policy_index=find_policy("GLOBAL", "GLOBAL", "GLOBAL", policy_name)
                if policy_index==-1:
                    temp_policy=copy.deepcopy(policy)
                    temp_policy["VSYS"]="GLOBAL"
                    temp_policy["from-zone"]="GLOBAL"
                    temp_policy["to-zone"]="GLOBAL"
                    temp_policy["policy-name"]=policy_name
                    temp_policy[property_type].append(propery_value)
                    policies_set.append(temp_policy)
                else:
                    temp_policy=policies_set[policy_index]
                    if property_type=="from-zone":
                        temp_policy["global-from-zone"].append(propery_value)
                    elif property_type=="to-zone":
                        temp_policy["global-to-zone"].append(propery_value)
                    else:
                        temp_policy[property_type].append(propery_value)
                    policies_set[policy_index]=temp_policy
            elif policy_property=='then':
                policy_index=find_policy("GLOBAL", "GLOBAL", "GLOBAL", policy_name)
                propery_value=data[7]
                temp_policy=policies_set[policy_index]
                temp_policy["action"].append(propery_value)


#export data to the file in CSV format
with open(f_out_name,"w",newline='') as f:
    csv_writer = csv.DictWriter(f,fieldnames=policy_description,delimiter=';')
    csv_writer.writeheader()
    csv_writer.writerows(policies_set)

         
            