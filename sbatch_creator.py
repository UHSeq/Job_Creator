#!/usr/bin/env python

import os
import json
import re

rsegments = r'-+\s\/.*'
rwhere = r'\s{2}Where:'
rdefault = r'\s{3}D:'
rload = r'\s{3}L:'
ruse = r'Use\s\"module'
rany = r'any of the '
rdemod = r'\s+\(D\)'
front3 = r'^\s{3}'
modbreaks = r'\s+'
rmodname = r'(\w+\-?\w+?\/\S+|R\/\S+)'
env_1 = r'source /home/${USER}/.bashrc'
env_2 = r'source activate '
# env_2 = r'source activate '

class Job:
    def __init__(self):
        self.cwd = os.getcwd()
        self.defaults_path = os.path.join(self.cwd, r'defaults.json')
        self.modtxt = os.path.join(self.cwd, r'modulelist.txt')
        self.load_header_defaults()
        self.load_modules()
        self.check_header_settings()
        self.add_modules()
        self.add_environment()
        self.lastline()
        self.print_to_shell()

    def add_environment(self):
        env_add = input("Do you need to set a Python environment? [y/n]: ")
        if re.match('y', env_add):
            print(f'Input the Python Enivronment\n{env_1}')
            mod_add = input(f'{env_2}:')
            self.env = [env_1, env_2 + mod_add]

    def add_modules(self):
        module_add = input("Do you want to add modules? [y/n]: ")
        if re.match('y', module_add):
            choosing = True
            while choosing:
                self.select_modules()
                finish = input("Finished? [y/n]: ")
                if re.match('y', finish):
                    choosing = False
                    print(self.modules)

    def adjust_header_settings(self):
        print("##Remember to not leave any whitespaces##")
        for key, value in self.settings.items():
            self.print_keyvalue_to_terminal(key, value)
            new_input = input(f"Set {key} to [leave blank for default]: ")
            if new_input == '':
                pass
            else:
                if re.search(r'\s+', new_input):
                    new_input = re.sub(r'\s+', r'', new_input)
                self.settings[key] = new_input
                if re.match(r'job-name', key):
                    setattr(self, "path", os.path.join(self.cwd, self.settings['job-name'] + '.sh'))
                    self.settings['output'] = r"%x_%j.out"
                    self.settings['error'] = r"%x_%j.err"
                if re.match(r'mail-user', key):
                    self.settings['mail-type'] = "ALL"

    def check_header_settings(self):
        chosing = True
        while chosing:
            print("\n###### DEFAULTS ######")
            for att, value in self.settings.items():
                self.print_keyvalue_to_terminal(att, value)
            use_defaults = input('######          ######\nDo you want to use the defaults[y/n]? : ')
            if re.match('y', use_defaults):
                chosing = False
            elif re.match('n', use_defaults):
                chosing = False
                self.settings_index = {}
                for index, (key, _) in enumerate(self.settings.items()):
                    self.settings_index[str(index)] = key
                self.adjust_header_settings()

    def lastline(self):
        print('\n###\nNow add the line to execute the script\nOr leave blank to input manually later')
        last_line = input("####: ")
        self.lastline = last_line

    def load_header_defaults(self):
        self.load_json('defaults', self.defaults_path)
        self.settings = {}
        self.modules = []
        for key, value in self.defaults.items():
            self.settings[key] = value
        delattr(self, "defaults")
        delattr(self, "defaults_path")
        setattr(self, "path", os.path.join(self.cwd, self.settings['job-name'] + '.sh'))

    def load_json(self, att_name, path):
        with open(path) as file:
            data = json.load(file)
            setattr(self, att_name, data)

    def load_modules(self):
        command = r'module avail > modulelist.txt'
        os.system(command)
        self.mod_list = []
        with open(self.modtxt) as file:
            for line in file:
                if re.search(rsegments, line) \
                or re.search(rdefault, line) \
                or re.search(rload, line) \
                or re.search(rwhere, line) \
                or re.search(ruse, line) \
                or re.match('\n', line) \
                or re.search(rany, line):
                    pass
                else:
                    line = re.sub(front3, '', line)
                    cluster = re.findall(rmodname, line)
                    for mod in cluster:
                        self.mod_list.append(mod)
        self.mod_list.sort()
        os.remove(self.modtxt)

    def print_to_shell(self):
        with open(self.path, 'w') as shell:
            shell.write('#!/bin/bash\n')
            for att, value in self.settings.items():
                if not value == None:
                    shell.write(f'#SBATCH --{att}={value}\n')
                else:
                    pass
            shell.write('\n\n')
            for mod in self.modules:
                shell.write(f'module load {mod}\n')
            # shell.write(self.env)
            for env in self.env:
                shell.write(f'{env}\n')
            shell.write(f'\n{self.lastline}')

    def print_keyvalue_to_terminal(self, att, value):
        print(f'{att} is set to {value}')

    def select_modules(self):
        for index, module in enumerate(self.mod_list):
            print(index, module)
        module_index = input("Input module [number]: ")
        module_index = int(module_index)
        self.modules.append(self.mod_list[module_index])
        del self.mod_list[module_index]


if __name__ in '__main__':
    job = Job()
