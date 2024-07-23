# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 10:05:59 2022

@author: CHCUK-02-Finn
"""

from configparser import ConfigParser
from datetime import datetime
import shutil
import time
import sys
import os

class Certificate_Holder:
    def __init__(self, config_file_ini):
        program_settings = config_file_ini
        cfg = ConfigParser()
        cfg.read(r'%s' %program_settings)
        for key in cfg['target paths']:
            if cfg['target paths'][key] != '':
                if key == 'cddis_certificate_path':
                    cert_target = cfg['target paths'][key]
                elif key == 'cddis_certificate_keeper':
                    cert_stored = cfg['target paths'][key]
                elif key == 'cddis_container_string':
                    cert_container = cfg['target paths'][key]
                elif key == 'cddis_certificate_name':    
                    cert_name = cfg['target paths'][key]
                elif key == 'cddis_remote_cert_dir':    
                    miss_dir = cfg['target paths'][key]
                elif key == 'cddis_routine_check':    
                    interval = cfg['target paths'][key]
            else:
                print('Certificate path is not set correctly: check configuration settings')
                
        self.certificate_path = cert_target
        self.certificate_bank = cert_stored
        self.certdir_string   = cert_container
        self.certificate_name = cert_name
        self.missing_cert_dir = miss_dir
        self.cert_upload_dir  = None 
        self.format_date      = '%H:%M:%S - %d/%m/%Y'
        self.wait_interval    = int(interval)
        self.certificate_dirs    = []
        self.certificate_records = []
        self.MEI_void            = []
        
    def core(self):
        print('\n\u00a9 2023 CHCTECH UK (CHCNAV-HUACE)\n')
        print('Data Upload certificate_holder initiated: ' + datetime.now().strftime(self.format_date) + '\ncurrent status: Running..')
        self.cert_saved()
        self.cert_checker()
    
    def cert_saved(self):
        os.chdir(self.certificate_path) #change to the hive where '_MEI' sits
        dirs_container = os.listdir()
        for existing_dir in dirs_container:
            if existing_dir.find(self.certdir_string, 0) != -1:
                self.certificate_dirs.append(existing_dir)
        for valid_dir in self.certificate_dirs:
            try:
                os.chdir(valid_dir) #access _MEI
                _MEI_container = os.listdir()
                if bool(_MEI_container) == False:
                    self.MEI_void.append(valid_dir)
            except:
                print('Could not access: ' + valid_dir)
            for existing_dir in _MEI_container:
                if existing_dir.find(self.missing_cert_dir, 0) != -1:
                    try:
                        os.chdir(existing_dir) #access 'certificate folder'
                        for file in os.listdir():
                            if file.find(self.certificate_name) != -1: #find existing certificates at _MEI
                                self.certificate_records.append([os.path.getctime(file), os.path.abspath(file)])
                        os.chdir('..')
                    except:
                        print('Could not access: ' + valid_dir)
            os.chdir('..')
            
        certificate_newest = [0, 'certificate_path_newest']
        if bool(self.certificate_records) == False:
            print('No certificate file' + self.certificate_name + ' has been found at: ' + self.certificate_path)
            sys.exit(0)
        else:
            for record in self.certificate_records:
                if record[0] >= certificate_newest[0]:
                    certificate_newest = [record[0], record[1]] #([1] <- original certificate location)
                    self.cert_saved_file = self.certificate_bank + '\\' + self.certificate_name
                    # self.cert_upload_dir = certificate_newest[1].replace(self.certificate_name,'') 
        shutil.copy(certificate_newest[1], self.certificate_bank) #save the certificate
        os.chdir(self.certificate_bank)
        logfile = open('certificate_records.txt','a')
        logfile.write('\ntransfered: '+ str(certificate_newest[0]) + ' ' + datetime.now().strftime(self.format_date) +'\n')   
        
    def cert_checker(self):
        while True:
            self.certificate_dirs = []
            base_time = datetime.now()
            timer_wait = self.wait_interval
            while (datetime.now() - base_time).total_seconds() <= timer_wait:
                time.sleep(1)
            
            os.chdir(self.certificate_path) #change to the hive where '_MEI' sits
            dirs_container = os.listdir()
            for existing_dir in dirs_container:
                if existing_dir.find(self.certdir_string, 0) != -1:
                    self.certificate_dirs.append(existing_dir)    
                    
            for valid_dir in self.certificate_dirs:
                try:
                    os.chdir(valid_dir) #access _MEI
                    _MEI_container = os.listdir()
                    if bool(_MEI_container) == False: #no files inside MEI
                        os.mkdir(self.missing_cert_dir)
                        shutil.copy(self.cert_saved_file, os.getcwd() + '\\' + self.missing_cert_dir)
                        self.alert()
                        
                    else: #files inside MEI
                        directory_found = False
                        for existing_obj in _MEI_container:
                            if existing_obj.find(self.missing_cert_dir, 0) != -1: #cert dir located
                                os.chdir(existing_obj)                            #enter 'certificate folder'
                                directory_found = True 
                                if bool(os.listdir()) == False: 
                                    shutil.copy(self.cert_saved_file, os.getcwd() + '\\' + self.certificate_name)
                                    self.alert()
                                    
                                else:
                                    files = os.listdir()
                                    cert_exists = 0
                                    for file in files:
                                        if file.find(self.certificate_name) != -1:
                                            if bool(os.stat(file).st_size) == True:
                                                cert_exists = 1
                                    if cert_exists == 0:
                                        shutil.copy(self.cert_saved_file, os.getcwd() + '\\' + self.certificate_name)
                                        self.alert()
                                        
                        if directory_found == False:
                            os.mkdir(self.missing_cert_dir)
                            shutil.copy(self.cert_saved_file, os.getcwd() + '\\' + self.missing_cert_dir)
                            self.alert()
                            
                    os.chdir(self.certificate_path)
                except:
                    print(f'Could not transfer the certificate {self.certificate_name} to the destination source')
                    
    def alert(self):
         print(
              '\n\'{}\' is a bundle of CA certificates that is used verify'.format(self.certificate_name) +
              '\n that the server is the correct site you\'re talking to' +
              '\n (when it presents its certificate in the SSL handshake)' +
              '\n the bundle should contain the certificates for the CAs you trust.' +
              '\n this bundle is at times referred to as the \'CA cert store\'.' +
              '\n this piece of software ensures that the designated ''CA certificate'' remains in active directories.'+
              '\n \u00a9 CHCTECH UK (CHCNAV-HUACE)'
              )
         print(
                    '\nfile: ' + self.cert_saved_file + ' \nuploaded to: ' + os.getcwd()
                    + '\ntime of event: ' + datetime.now().strftime(self.format_date) 
                    + '\n\ncurrent status: Running..'
              )
                    
Certificate_Holder('certificate_settings.ini').core()


