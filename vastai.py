import requests
import urllib.parse
import json

queryString = {
    "disk_space": {"gte": 16},
    "duration": {"gte": 262144},
    "datacenter": {"eq": False},
    "verified": {"eq": True},
    "rentable": {"eq": True},
    "sort_option": {"0": ["dlperf_per_dphtotal", "desc"]},
    "order": [["dlperf_per_dphtotal", "desc"]],
    "num_gpus": {"gte": 0, "lte": 1000000},
    "allocated_storage": 16,
    "cuda_max_good": {"gte": "11.8"},
    "cpu_arch": {"in": ["amd64"]},
    "limit": 1000000,
    "extra_ids": [],
    "type": "ask"
}

# MD5 hashrate in H/s. "-1" = unknown/unsupported
# https://docs.google.com/spreadsheets/d/1tzmCx8TX3208lO0dY91YJuS9EmUictUnONGDM7snIHU/edit#gid=0

hashrateTable = {
    "A10":              45785700000,
    "A100 PCIE":        64935200000,
    "A100 SXM4":        65855800000,
    "A100X":            52693600000,
    "A40":              64565900000,
    "GH200 SXM":        -1,
    "GTX 1080 Ti":      35255900000,
    "H100 PCIE":        87530600000,
    "H100 SXM":         116500000000,
    "L40":              39827900000,
    "L40S":             -1,
    "GTX 1050 Ti":      6536100000,
    "GTX 1060":         11560200000,
    "GTX 1070":         17907600000,
    "GTX 1070 Ti":      23729300000,
    "GTX 1080":         25114100000,
    "GTX 1660 S":       17956000000,
    "GTX 1660 Ti":      18939000000,
    "RTX 2060":         24005900000,
    "RTX 2060S":        28847300000,
    "RTX 2070S":        30197000000,
    "RTX 2080 Ti":      52990500000,
    "RTX 3060":         25021200000,
    "RTX 3060 laptop":  -1,
    "RTX 3060 Ti":      32061800000,
    "RTX 3070":         38807400000,
    "RTX 3070 Ti":      43319600000,
    "RTX 3080":         54033100000,
    "RTX 3080 Ti":      66673100000,
    "RTX 3090":         65079100000,
    "RTX 3090 Ti":      79738800000,
    "RTX 4060 Ti":      41451300000,
    "RTX 4070":         28582100000,
    "RTX 4070S":        -1,
    "RTX 4070 Ti":      67809500000,
    "RTX 4070S Ti":     -1,
    "RTX 4080":         98262800000,
    "RTX 4080S":        95465600000,
    "RTX 4090":         164100000000,
    "RTX 4000Ada":      -1,
    "RTX 5000Ada":      -1,
    "RTX 6000Ada":      130200000000,
    "RTX A2000":        17261700000,
    "RTX A4000":        25307200000,
    "RTX A5000":        39590800000,
    "RTX A6000":        68198700000,
    "Tesla P40":        -1,
    "Tesla P100":       27159500000,
    "Tesla V100":       56376200000,
    "Titan V":          -1,
    "Titan RTX":        61931600000,
    "Q RTX 8000":       52298000000,
}

# Easily filterable/searchable GPUs in vast
# Any that aren't on this list may need to be accessed through the API rather than the website (stupidly)
searchable_gpus = {
    "H100 PCIE",
    "H100 SXM",
    "L40"
    "RTX 6000Ada",
    "RTX 4090",
    "RTX 4080",
    "RTX 4080 S",
    "RTX 4070",
    "A100 PCIE",
    "A100 SXM4",
    "A100X",
    "A40",
    "A10",
    "RTX A6000",
    "RTX A5000",
    "RTX A4000",
    "RTX 3090",
    "RTX 5000Ada",
    "RTX 3090 Ti",
    "RTX 3080 Ti",
    "RTX 3080",
    "RTX 3070",
    "RTX 3060",
    "Q RTX 8000",
    "Tesla V100"    
}

import argparse

parser = argparse.ArgumentParser(prog='vast.ai', description="An application to guess the most price-effective vast.ai instance for Hashcat, based on MD5 benchmark speeds.", epilog="If instances aren't showing up in the GUI, make sure you scroll to the bottom and click \"Show More\"")
parser.add_argument("--hashrate-min", help="Set the minimum hashrate (GH/s)", default = 0, type=int)
parser.add_argument("--hashrate-max", help="Set the maximum hashrate (GH/s)", default = 10**10, type=int)
parser.add_argument("--cost-min", help="Set the minimum cost per hour ($/hr)", default = 0, type=int)
parser.add_argument("--cost-max", help="Set the maximum cost per ($/hr)", default = 10**10, type=int)
parser.add_argument("--instances", help="Set the amount of instances to show", default = 15, type=int)
parser.add_argument("--all-instances", help="Show instances that are hard to find on the website (Default: False)", default = "false", type=str.lower) # argparse doesn't handle bools well
parser.add_argument("--datacentre", help="Only show datacentre-hosted instances (Default: False)", default = "false", type=str.lower) # argparse doesn't handle bools well

args = parser.parse_args()

if (args.datacentre == 'true'):
    queryString.datacenter["eq"] = True

request = requests.get(f"https://cloud.vast.ai/api/v0/bundles/?q={urllib.parse.quote(json.dumps(queryString))}")

if (request.status_code != 200):
    print(f"Failed to get the API data! HTTP: {request.status_code}")
    exit(1)

instances = request.json()["offers"]

machines = {}

for instance in instances:

    if (instance["gpu_name"] not in hashrateTable):
        print(f'Unknown GPU: {instance["gpu_name"]}')
        continue

    if (((instance["gpu_name"] in searchable_gpus) or (args.all_instances == "true")) == False):
        continue

    if (hashrateTable[instance["gpu_name"]] != -1):
        hashrate = int(hashrateTable[instance["gpu_name"]] * instance["num_gpus"])
        costPerHour = instance["discounted_dph_total"]

        if (hashrate < (args.hashrate_min * 10**9) or hashrate > (args.hashrate_max * 10**9)):
            continue

        if (costPerHour < args.cost_min or costPerHour > args.cost_max):
            continue

        machines[instance["id"]] = {
                                    'GPU Name': instance["gpu_name"],
                                    'GPU Count': instance["num_gpus"],
                                    'Hashrate': hashrate,
                                    'Cost Per Hour': costPerHour,
                                    'Cost Per Petahash': (10**15 / hashrate) * (instance["discounted_dph_total"] / 3600)
                                   }
        
# Sort by $ per PH
topMachines = dict((sorted(machines.items(), key=lambda x: x[1]['Cost Per Petahash'], reverse=False))[:args.instances])

# Print ASCII Art table of the most cost-effective machines
print("+-----------------+--------+------------------+---------------+-----------------+")
print("| {:^15} | {:^6} | {:^16} | {:^13} | {:^15} |".format("GPU Name", "GPUs", "Hashrate (GH/s)", "Cost Per Hour", "$ Per Petahash"))
print("+-----------------+--------+------------------+---------------+-----------------+")

for i in topMachines:
    print("| {:^15} | {:^6} | {:^16.2f} | {:^13.3f} | {:^15.3f} |".format(topMachines[i]["GPU Name"], topMachines[i]["GPU Count"], topMachines[i]["Hashrate"] / 1_000_000_000, topMachines[i]["Cost Per Hour"], topMachines[i]["Cost Per Petahash"]))

print("+-----------------+--------+------------------+---------------+-----------------+")