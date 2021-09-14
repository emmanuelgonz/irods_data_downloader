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
                        choices=['10', '11', '12'])

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

    return parser.parse_args()


# --------------------------------------------------
def get_dict():
    
    irods_dict = {
        'server_path': '/iplant/home/shared/phytooracle/',

        'season': {
            '10': 'season_10_lettuce_yr_2020',
            '11': 'season_11_sorghum_yr_2020',
            '12': 'season_12_sorghum_soybean_sunflower_tepary_yr_2021'
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

    result = sp.run(f'ilocate {os.path.join(data_path, "%", f"%{sequence}")}', stdout=sp.PIPE, shell=True)
    files = result.stdout.decode('utf-8').split('\n')

    return files


# --------------------------------------------------
def download_files(files):
    
    for item in files: 
        
        if not 'deprecated' in item:

            try:
                item = os.path.normpath(item)
                date = item.split(os.sep)[-2]
                os.makedirs(date)
                sp.call(f'iget -KPVT {item}', shell=True)

                if '.tar.gz' in item: 

                    p = sp.call(f'tar -xzvf {os.path.basename(item)} -C {date}', shell=True, 
                                                                                stdout=sp.PIPE, 
                                                                                stderr=sp.PIPE)
                                                                                
                    if p.returncode != 0:

                        sp.call(f'tar -xvf {os.path.basename(item)} -C {date}', shell=True)
                    
                elif '.tar' in item:
                    sp.call(f'tar -xvf {os.path.basename(item)} -C {date}', shell=True)

                else:
                    continue
                
                sp.call(f'rm {os.path.basename(item)}', shell=True)

            except:
                pass


# --------------------------------------------------
def main():
    """Download data here"""
    args = get_args()

    # Get dictionary to pull path components. 
    irods_dict = get_dict()

    # Create iRODS path from components. 
    data_path = os.path.join(irods_dict['server_path'], irods_dict['season'][args.season], irods_dict['level'][args.level], irods_dict['sensor'][args.sensor])
    
    # Get list of all files that match a character sequence.
    print(f'Searching for files matching "{args.sequence}". Note: This process may take 1-5 minutes.')
    files = get_file_list(data_path, args.sequence)
    print('Matches obtained.')

    # Prepare to download data.
    out_path = os.path.join(args.outdir, irods_dict['season'][args.season], irods_dict['sensor'][args.sensor])
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    os.chdir(out_path)

    # Download files.
    for item in files: 
        print(f'Downloading {item}.')
        download_files(files)


# --------------------------------------------------
if __name__ == '__main__':
    main()
