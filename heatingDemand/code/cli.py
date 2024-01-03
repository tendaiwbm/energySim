"""
@author: TM
"""

import os
from pyepw.epw import EPW

os.chdir('../data/NLD_OV_Heino.062780_TMYx2007-2021')
epw = []

with open('../data/Heino.epw','r') as epww:
    epw = epww.readlines()

location = epw[0].rstrip('\n').split(',')    
epw = epw[8:]
epww = []
for i in range(len(epw)):
    epw[i] = (epw[i].rstrip('\n').split(','))
    epw[i].pop(5)

i = 1
cli_lines = {}

for item in epw:
    cli_lines[str(i)] = [(int(item[2])),(int(item[1])),(int(item[3])),(float(item[14])),
                         (float(item[13])),(float(item[5])),(float(item[5])),(float(item[20])),
                         (int(item[19])),(int(item[7])),(float(item[-2])),int((float(item[21])*0.8))]
    i += 1
del epw

header = ['dm','m','h','G_Dh','G_Bn','Ta','Ts','FF','DD','RH','RR','N']  
i = 1
with open('../data/Heino.cli','w') as cli:
    cli.write(location[1]+'\n')
    cli.write('{},{},{},+{}\n'.format(float(location[6]),float(location[7]),float(location[9]),int(float(location[8]))))
    cli.write('\n')
    cli.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.
              format(header[0],header[1],header[2],header[3],
                     header[4],header[5],header[6],header[7],
                     header[8],header[9],header[10],header[11]))
    while i < len(cli_lines):
        cli.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.
              format(cli_lines[str(i)][0],cli_lines[str(i)][1],cli_lines[str(i)][2],cli_lines[str(i)][3],
                     cli_lines[str(i)][4],cli_lines[str(i)][5],cli_lines[str(i)][6],cli_lines[str(i)][7],
                     cli_lines[str(i)][8],cli_lines[str(i)][9],cli_lines[str(i)][10],cli_lines[str(i)][11]))
        i += 1
    
