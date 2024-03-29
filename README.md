# IRODS data downloader

## Purpose:
This repo is meant to allow recursive downloads from [PhytoOracle's CyVerse Data Store](https://de.cyverse.org/data/ds/iplant/home/shared/phytooracle?selectedOrder=asc&selectedOrderBy=name&selectedPage=0&selectedRowsPerPage=100).

## Example: 
To download all season 10 orthomosaics, you would need to the specify the level in which these data are found and the unique sequence (wildcard). The command would be as follows: 
```
./irods_download.py --season 15 --sensor RGB --level 1 --sequence cubic.tif -c lettuce
```
Data will be downloaded and uncompressed in the ```irods_data/<season>/<sensor>/<date>``` directory by default, unless otherwise specified. The original compressed (tarball) will be deleted to reduce storage space usage.

## Flags: 
* -sea, --season (str, required)
    * Selected season to download data for.
        * Options = 10, 11, 12
* -sen, --sensor (str, required)
    * Sensor to download data for.
        * Options = FLIR, RGB, 3D, and PS2
*  -lev, --level (str, required)
    * Data level to download data for. 
        * Options = 0, 1, 2, 3, or 4 
* -seq, --sequence (str, required)
    * Unique sequence to use as a wildcard. 
* -out, --outdir (str, optional)
    * Output directory. Default is ```irods_data```.
* -c, --crop
    * Crop name (lettuce, sorghum, etc.)    
