#!/usr/bin/env python

import os
import csv
import random
import subprocess
import argparse

par = argparse.ArgumentParser(description="Download and process Physionet Datasets")

par.add_argument("-dl", nargs="+",
                 dest="dataset_list",
                 default=[],
                 choices=["nsrdb", "apnea-ecg", "mitdb", "afdb", "svdb"],
                 help="The list of datasets to download")

args = par.parse_args()
dataset_list = args.dataset_list


def fetch_data(db=None):
    """
    nsrdb normal sinus rhythm
    apnea
    mitdb arrhythmia
    afdb atrial fibrillation
    svdb supraventricular arrhythmia 
    """

    physionet = {
        "nsrdb": ["16265", "16272", "16273", "16420", "16483", "16539", "16773",
                  "16786", "16795", "17052", "17453", "18177", "18184", "19088",
                  "19090", "19093", "19140", "19830"],
        "apnea-ecg": ["a01", "a01er", "a01r", "a02", "a02er", "a02r", "a03",
                      "a03er", "a03r", "a04", "a04er", "a04r", "a05", "a06",
                      "a07", "a08", "a09", "a10", "a11", "a12", "a13", "a14",
                      "a15", "a16", "a17", "a18", "a19", "a20", "b01", "b01er",
                      "b01r", "b02", "b03", "b04", "b05", "c01", "c01er", "c01r",
                      "c02", "c02er", "c02r", "c03", "c03er", "c03r", "c04",
                      "c05", "c06", "c07", "c08", "c09", "c10", "x01", "x02",
                      "x03", "x04", "x05", "x06", "x07", "x08", "x09", "x10",
                      "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18",
                      "x19", "x20", "x21", "x22", "x23", "x24", "x25", "x26",
                      "x27", "x28", "x29", "x30", "x31", "x32", "x33", "x34", "x35"],
        "mitdb": ["100", "101", "102", "103", "104", "105", "106", "107", "108",
                  "109", "111", "112", "113", "114", "115", "116", "117", "118",
                  "119", "121", "122", "123", "124", "200", "201", "202", "203",
                  "205", "207", "208", "209", "210", "212", "213", "214", "215",
                  "217", "219", "220", "221", "222", "223", "228", "230", "231",
                  "232", "233", "234"],
        "afdb": ["04015", "04043", "04048", "04126", "04746", "04908", "04936",
                 "05091", "05121", "05261", "06426", "06453", "06995", "07162",
                 "07859", "07879", "07910", "08215", "08219", "08378", "08405",
                 "08434", "08455"],
        "svdb": ["800", "801", "802", "803", "804", "805", "806", "807", "808",
                 "809", "810", "811", "812", "820", "821", "822", "823", "824",
                 "825", "826", "827", "828", "829", "840", "841", "842", "843",
                 "844", "845", "846", "847", "848", "849", "850", "851", "852",
                 "853", "854", "855", "856", "857", "858", "859", "860", "861",
                 "862", "863", "864", "865", "866", "867", "868", "869", "870",
                 "871", "872", "873", "874", "875", "876", "877", "878", "879",
                 "880", "881", "882", "883", "884", "885", "886", "887", "888",
                 "889", "890", "891", "892", "893", "894"]
    }

    dataset_dir = "datasets/raws"
    
    def check_folder_existance():
        if not os.path.isdir(dataset_dir):
            print("Directory {} not found".format(dataset_dir))
            print("Creating now...")
            os.makedirs(dataset_dir)

        for database in physionet:
            folder = os.path.join(dataset_dir, database)
            if not os.path.isdir(folder):
                print("Directory {} not found".format(folder))
                print("Creating now...")
                os.makedirs(folder)

    def rdsamp_installed():
        try:
            subprocess.call(["rdsamp", "-h"], stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
            return True
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print("rdsamp not installed")
                return False

        print("rdsamp installed check failed")
        return False

    def remove_unwanted_datasets():
        if dataset_list:
            unwanted_ds = physionet.keys() - dataset_list
            for ds in unwanted_ds:
                physionet.pop(ds, None)

    if db is not None:
        dataset_list.append(db)
    remove_unwanted_datasets()
    check_folder_existance()
    if not rdsamp_installed():
        sys.exit(1)

    for database, samples in physionet.items():
        print("Downloading {}".format(database))
        database_dir = os.path.join(dataset_dir, database)
        for sample in samples:
            csv_file_path = os.path.join(database_dir, sample) + ".csv"
            if os.path.exists(csv_file_path):
                print("File {} exists. Skipping download...".format(csv_file_path))
            else:
                sample_path = os.path.join(database, sample)
                cmd = ("rdsamp -r {} -c -H -f 0" +
                       " -v -pe > {}").format(sample_path, csv_file_path)
                try:
                    print("Downloading with command {}...".format(cmd))
                    subprocess.check_call(cmd, shell=True)
                except Exception as e:
                    print("Failed to execute command: {} with exception: {}".format(cmd, e))
                    if os.path.exists(csv_file_path):
                        os.remove(csv_file_path)

            ann_file_path = os.path.join(database_dir, sample) + ".txt"
            if os.path.exists(ann_file_path):
                print("File {} exists. Skipping download...".format(ann_file_path))
            else:
                sample_path = os.path.join(database, sample)
                cmd = ("rdann -r {} -f 0 -a atr" +
                       " -v > {}").format(sample_path, ann_file_path)
                try:
                    print("Downloading with command {}...".format(cmd))
                    subprocess.check_call(cmd, shell=True)
                except Exception as e:
                    print("Failed to execute command: {} with exception: {}".format(cmd, e))
                    if os.path.exists(ann_file_path):
                        os.remove(ann_file_path)

        if os.path.isdir(database_dir) and not os.listdir(database_dir):
            cmd = "rm -rf {}".format(database_dir)
            subprocess.check_call(cmd, shell=True)
    print("Done")


def get_data(ecg_name):
    print("Getting data...")
    raw_dir = "datasets/raws"
    sample_dir = "datasets/samples"
    RANGE = 130
    
    ecg_dirs = os.listdir(raw_dir)

    # according to codes in MIT BIH arrhythmias Database Directory
    ecg_classes = { 'N': 0, 'R': 0, 'L': 0, 'e': 0, 'j': 0,
                    'A': 1, 'a': 1, 'J': 1, 'S': 1,
                    'V': 2, 'E': 2,
                    'F': 3,
                    '/': 4, 'f': 4, 'Q': 4 }
    
    if not os.path.isdir(sample_dir):
        print("Directory {} not found".format(sample_dir))
        print("Creating now...")
        os.makedirs(sample_dir)
    for i in [0, 1, 2, 3, 4]:
        class_dir = sample_dir + '/' + str(i)
        if not os.path.isdir(class_dir):
            print("Directory {} not found".format(class_dir))
            print("Creating now...")
            os.makedirs(class_dir)

    print("Getting {}".format(ecg_name))
    record_dir = os.path.join(raw_dir, ecg_name)
    for record in sorted(os.listdir(record_dir)):
        if record.endswith('.csv'):
            # read record
            t, ch1, ch2 = [], [], []
            record_len = 0
            record_path = os.path.join(record_dir, record)
            print(record_path)
            with open(record_path) as read_raw_file:
                reader = csv.reader(read_raw_file)
                # skip headers
                reader.__next__()
                reader.__next__()
                for i, row in enumerate(reader):
                    t.append(row[0])
                    ch1.append(row[1])
            with open(record_path) as read_raw_file:
                record_len = sum(1 for line in read_raw_file) - 1

            # read annotation
            bname = os.path.splitext(record)[0]
            annotate_path = os.path.join(record_dir, bname+'.txt')
            if not os.path.exists(annotate_path):
                continue
            tl, ecgtype = [], []
            with open(annotate_path) as read_raw_file:
                lines = read_raw_file.readlines()
                # skip header
                for line in lines[1:]:
                    row = line.split()
                    time = int(row[1])
                    if time > RANGE and time <= record_len - RANGE:
                        tl.append(time)
                        ecgtype.append(row[2])

            # write sample files
            for index, pi in enumerate(tl):
                data = ch1[pi-RANGE:pi+RANGE]
                if not ecgtype[index] in ecg_classes:
                    continue
                class_name = str(ecg_classes[ecgtype[index]])
                output_path = sample_dir+'/'+class_name+'/'+bname+'_'+str(index)+'.txt'
                print("Writing {}".format(output_path))
                of = open(output_path, 'w')
                for d in data:
                    of.write(d + '\n')
                of.close()

fetch_data('mitdb')
get_data('mitdb')
