# vastai-sorter
Sort instances based on Hashcat price-to-hashrate. Tested on Python 3.8.10.

## Usage:
```
$ python3 vastai.py --help
usage: vast.ai [-h] [--hashrate-min HASHRATE_MIN] [--hashrate-max HASHRATE_MAX] [--cost-min COST_MIN] [--cost-max COST_MAX] [--instances INSTANCES] [--all-instances ALL_INSTANCES]
               [--datacentre DATACENTRE]

An application to guess the most price-effective vast.ai instance for Hashcat, based on MD5 benchmark speeds.

optional arguments:
  -h, --help            show this help message and exit
  --hashrate-min HASHRATE_MIN
                        Set the minimum hashrate (GH/s)
  --hashrate-max HASHRATE_MAX
                        Set the maximum hashrate (GH/s)
  --cost-min COST_MIN   Set the minimum cost per hour ($/hr)
  --cost-max COST_MAX   Set the maximum cost per ($/hr)
  --instances INSTANCES
                        Set the amount of instances to show
  --all-instances ALL_INSTANCES
                        Show instances that are hard to find on the website (Default: False)
  --datacentre DATACENTRE
                        Only show datacentre-hosted instances (Default: False)

If instances aren't showing up in the GUI, make sure you scroll to the bottom and click "Show More"
```
