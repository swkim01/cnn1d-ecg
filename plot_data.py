#!/usr/bin/env python

import os
import csv
import random
import subprocess
import argparse
import matplotlib.pyplot as plt

par = argparse.ArgumentParser(description="Download and process Physionet Datasets")

par.add_argument("-dl", nargs="+",
                 dest="dataset_list",
                 default=[],
                 choices=["nsrdb", "apnea-ecg", "mitdb", "afdb", "svdb"],
                 help="The list of datasets to download")

args = par.parse_args()
dataset_list = args.dataset_list

def plot_data(ecg_name):
    print("Plotting data...")
    raw_dir = "datasets/raws"
    
    ecg_dirs = os.listdir(raw_dir)
    
    print("Plotting {}".format(ecg_name))
    record_dir = os.path.join(raw_dir, ecg_name)
    for record in sorted(os.listdir(record_dir)):
        if record.endswith('.csv'):
            t, ch1, ch2 = [], [], []
            record_path = os.path.join(record_dir, record)
            print(record_path)
            with open(record_path) as read_raw_file:
                reader = csv.reader(read_raw_file)
                # skip headers
                reader.__next__()
                reader.__next__()
                for i, row in enumerate(reader):
                    if i >= 3600 and i < 7200:
                        t.append(row[0])
                        ch1.append(row[1])
                        ch2.append(row[2])
            fig, ax = plt.subplots(2)
            ax[0].set_title(record)
            ax[0].plot(ch1)
            ax[1].plot(ch2)

            bname = os.path.splitext(record)[0]
            annotate_path = os.path.join(record_dir, bname+'.txt')
            if os.path.exists(annotate_path):
                with open(annotate_path) as read_raw_file:
                    # skip header
                    #read_raw_file.readlines()
                    i = 0
                    lines = read_raw_file.readlines()
                    tl, ecgtype = [], []
                    for line in lines[1:]:
                        row = line.split()
                        time = int(row[1])
                        if time >= 3600  and time < 7200:
                            tl.append(time-3600)
                            ecgtype.append(row[2])
                    for ti, et in zip(tl, ecgtype):
                        print(ti, et)
                        ax[0].text(ti, ch1[ti], et)

            plt.tight_layout()
            plt.show()

#fetch_data()
plot_data('mitdb')
