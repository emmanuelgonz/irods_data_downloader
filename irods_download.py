#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez
Date   : 2021-09-13
Purpose: Download gantry data 
"""

import argparse
import os
import sys
import subprocess as sp
import re
from datetime import datetime

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='iRODS data downloader',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-sea',
                        '--season',
                        help='Season to download. Choices are 10, 11, or 12.',
                        metavar='str',
                        type=str,
                        required=True, 
                        choices=['10', '11', '12', '13', '14', '15'])

    parser.add_argument('-sen',
                        '--sensor',
                        help='Sensor to download. Choices are FLIR, PS2, RGB, or 3D.',
                        metavar='str',
                        type=str,
                        required=True,
                        choices=['FLIR', 'PS2', 'RGB', '3D'])

    parser.add_argument('-lev',
                        '--level',
                        help='Data level to download. Choices are 0, 1, 2, 3, or 4.',
                        metavar='str',
                        type=str,
                        required=True,
                        choices=['0', '1', '2', '3', '4'])

    parser.add_argument('-seq',
                        '--sequence',
                        help='Sequence to grep. For example "_ortho.tif".',
                        metavar='str',
                        type=str,
                        required=True)

    parser.add_argument('-out',
                        '--outdir',
                        help='Output directory.',
                        metavar='str',
                        type=str,
                        default='irods_data')
    
    parser.add_argument('-c',
                        '--crop',
                        help='Crop name.',
                        metavar='str',
                        type=str,
                        default=None)
    
    return parser.parse_args()


# --------------------------------------------------
def get_dict():
    
    irods_dict = {
        'server_path': '/iplant/home/shared/phytooracle/',

        'season': {
            '10': 'season_10_lettuce_yr_2020',
            '11': 'season_11_sorghum_yr_2020',
            '12': 'season_12_sorghum_soybean_sunflower_tepary_yr_2021',
            '13': 'season_13_lettuce_yr_2022',
            '14': 'season_14_sorghum_yr_2022',
            '15': 'season_15_lettuce_yr_2022',
            '16': 'season_16_sorghum_yr_2023'
        },

        'level': {
            '0': 'level_0', 
            '1': 'level_1',
            '2': 'level_2',
            '3': 'level_3',
            '4': 'level_4'
        },

        'sensor': {
            'FLIR': 'flirIrCamera',
            'PS2': 'ps2Top',
            'RGB': 'stereoTop',
            '3D': 'scanner3DTop'
        }
    }

    return irods_dict


# --------------------------------------------------
def get_file_list(data_path, sequence):

    result = sp.run(f'ilocate {os.path.join(data_path, "%", f"{sequence}")}', stdout=sp.PIPE, shell=True)
    files = result.stdout.decode('utf-8').split('\n')

    return files


# --------------------------------------------------
def download_files(item, out_path):

    
    
    # for item in files: 
        
    os.chdir(out_path)

    if not 'deprecated' in item:

        try:
            item = os.path.normpath(item)

            try:

                match_str = re.search(r'\d{4}-\d{2}-\d{2}__\d{2}-\d{2}-\d{2}-\d{3}', item)
                date = match_str.group()
                # date = datetime.strptime(match_str.group(), '%Y-%m-%d').date()
            except:
                match_str = re.search(r'\d{4}-\d{2}-\d{2}', item)
                date = datetime.strptime(match_str.group(), '%Y-%m-%d').date()
                date = str(date)

            print(f"Found item {item}.")

            if not os.path.isdir(date):
                print(f"Making directory {date}.")
                os.makedirs(date)


            if '.tar.gz' in item: 
                print(f"Downloading {item}.")
                sp.call(f'iget -KPVT {item}', shell=True)

                print(f"Extracting {item}.")
                ret = sp.call(f'tar -xzvf {os.path.basename(item)} -C {date}', shell=True)

                if ret != 0:
                    print(f"Reattempting to extract {item}.")
                    sp.call(f'tar -xvf {os.path.basename(item)} -C {date}', shell=True)

                sp.call(f'rm {os.path.basename(item)}', shell=True)

            elif '.tar' in item:
                print(f"Downloading {item}.")
                sp.call(f'iget -KPVT {item}', shell=True)
                
                print(f"Extracting {item}.")
                sp.call(f'tar -xvf {os.path.basename(item)} -C {date}', shell=True)
                sp.call(f'rm {os.path.basename(item)}', shell=True)

            else:
                os.chdir(date)
                sp.call(f'iget -KPVT {item}', shell=True)
            
        except:
            pass


# --------------------------------------------------
def main():
    """Download data here"""
    args = get_args()
    cwd = os.getcwd()

    # Get dictionary to pull path components. 
    irods_dict = get_dict()

    # Create iRODS path from components. 
    data_path = os.path.join(irods_dict['server_path'], irods_dict['season'][args.season], irods_dict['level'][args.level], irods_dict['sensor'][args.sensor])
    if args.crop:
        data_path = os.path.join(irods_dict['server_path'], irods_dict['season'][args.season], irods_dict['level'][args.level], irods_dict['sensor'][args.sensor], args.crop)
    # Get list of all files that match a character sequence.
    print(f'Searching for files matching "{os.path.join(data_path, args.sequence)}". Note: This process may take a few minutes.')
    files = get_file_list(data_path, args.sequence)
    print('Matches obtained.')

    # Prepare to download data.
    out_path = os.path.join(args.outdir, irods_dict['season'][args.season], irods_dict['sensor'][args.sensor])
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    os.chdir(out_path)

    # Download files.
    for item in files: 
        # print(f'Downloading {item}.')
        download_files(item=item, out_path=os.path.join(cwd, out_path))


# --------------------------------------------------
if __name__ == '__main__':
    main()
