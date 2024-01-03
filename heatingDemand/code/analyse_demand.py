# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:20:22 2022

@author: TM
"""
import psycopg2
import matplotlib.pyplot as plt
import heapq
import numpy


def getEnergyDemand(cursor,scenario):
    
    # get gmlid and yearly energy demand value for energydemand objects
    query = '''select co.gmlid, gen.realval from cdb.cityobject as co
               join cdb.cityobject_genericattrib as gen
               on co.id = gen.cityobject_id
               where co.objectclass_id = 50033 
               and co.name LIKE '{}%' '''.format(scenario)
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows
    
def energyDifference(scenarios):
    
    mediumDiff = []
    advDiff = []
    
    # mediumRefurb - statusQuo; advRefurb - statusQuo
    for i in range(len(scenarios[list(scenarios.keys())[0]])):
        try:
            mediumDiff.append(((scenarios['mediumRefurb'][i][1]-scenarios['statusQuo'][i][1])/scenarios['statusQuo'][i][1])*100)
        except:
            mediumDiff.append(0)
    for i in range(len(scenarios[list(scenarios.keys())[0]])):
        try:
            advDiff.append(((scenarios['advRefurb'][i][1]-scenarios['statusQuo'][i][1])/scenarios['statusQuo'][i][1])*100)
        except:
            advDiff.append(0)
    
    # find EnergyDemand object(s) with biggest decrease 
    mediumId = {}
    advId = {}
    for i in range(len(mediumDiff)):
        if mediumDiff[i] == min(mediumDiff):
            mediumId[scenarios['mediumRefurb'][i][0]] = [scenarios['statusQuo'][i][1],scenarios['mediumRefurb'][i][1],mediumDiff[i]]
        if advDiff[i] == min(advDiff):
            advId[scenarios['advRefurb'][i][0]] = [scenarios['statusQuo'][i][1],scenarios['advRefurb'][i][1],advDiff[i]]
    
def bldgMonthlyGraph(cursor):
    
    # get regulartimeseries values for NL.IMBAG.Pand.1742100000000602
    query = '''select rgt.values_ from ng_regulartimeseries as rgt
               join ng_energydemand as ed on rgt.id = ed.energyamount_id
               join cityobject as co on ed.id = co.id
               where co.name LIKE 'statusQuo%month%' and co.gmlid LIKE '%NL.IMBAG.Pand.1742100000000602%' '''
    cursor.execute(query)
    values = cursor.fetchall()[0][0]
    values = values.rstrip(' ').split(' ')
    
    for i in range(len(values)):
         values[i] = float(values[i])
    
    # plot monthly values and save figure
    months = ['Jan','Feb','Mar','Apr','May','June','July','Aug','Sep','Oct','Nov','Dec']
    plt.plot(months,values,color='red',marker='o')
    plt.title('Monthly Heating Demand for NL.IMBAG.Pand.1742100000000602')
    plt.xlabel('Month',fontsize=8)
    plt.ylabel('Energy Demand (kWh/month)',fontsize=8)
    plt.xticks(rotation=90,ha='left',fontsize=8)
    plt.yticks(fontsize=7)
    plt.grid(True)
    plt.savefig('../output/NL.IMBAG.Pand.1742100000000602.png',dpi=250,bbox_inches='tight')
    plt.clf()

def volDemandGraph(cursor,scenarios):
    
    # get gmlid and volume of buildings
    query = '''select co.gmlid, gen.realval from cityobject as co
               join cityobject_genericattrib as gen on co.id = gen.cityobject_id
               where gen.attrname = 'lod2_volume' order by gen.realval desc '''
    cursor.execute(query)
    rows = cursor.fetchall()
    data= {}
    buildings = {}
    for row in rows:
        buildings[row[0]] = row[1]
    
    # get yearly energy demand for energydemand objects
    # combine with buildings and volumes
    # extract first 10 energydemand objects according to volume in descending order
    for scenario in scenarios:
        query = '''select co.gmlid,gen.realval from cityobject as co
                   join cityobject_genericattrib as gen on co.id = gen.cityobject_id
                   where co.name LIKE '{}%yearly' '''.format(scenario)
        cursor.execute(query)
        rows = cursor.fetchall()
        energyDemand = {}
        for row in rows:
            energyDemand[row[0]] = [row[1]]
        
        heap = []
        for key1 in list(energyDemand.keys()):
            for key2 in list(buildings.keys()):
                if key2 in key1:
                    energyDemand[key1].append(buildings[key2])
                    heap.append([buildings[key2],energyDemand[key1][0],key1])
                    
        data[scenario] = heapq.nlargest(10,heap)
    
    # plot bar graph of refurbishment scenarios for the 10 objects and save figure
    statusQuo = []
    mediumRefurb = []
    advRefurb = []
    building = []
    for i in data['statusQuo']:
        building.append(i[2][14:44])
        statusQuo.append(i[1])
    for i in data['mediumRefurb']:
        mediumRefurb.append(i[1])
    for i in data['advRefurb']:
        advRefurb.append(i[1])
    
    barWidth = 0.25
    bar1 = numpy.arange(len(advRefurb))
    bar2 = [x + barWidth for x in bar1]
    bar3 = [x + barWidth for x in bar2]
    
    # plot data
    plt.bar(bar1,statusQuo,color='r',width=barWidth,edgecolor='grey',label='statusQuo')
    plt.bar(bar2,mediumRefurb,color='g',width=barWidth,edgecolor='grey',label='mediumRefurb')
    plt.bar(bar3,advRefurb,color='b',width=barWidth,edgecolor='grey',label='advRefurb')
    plt.xlabel('Building',labelpad=10,fontsize=8)
    plt.ylabel('Energy Demand (MWh/a)',fontsize=8)
    plt.xticks([r + barWidth for r in range(len(advRefurb))],building,rotation=90,ha='left',fontsize=8)
    plt.title('Yearly Heating Demand')
    plt.legend(fontsize=8)
    plt.savefig('../output/volume_scenario_demand_diff.png',dpi=250,bbox_inches='tight')
    
def insert_genericattrib(cursor,row,connection):
    
    query = '''INSERT INTO cityobject_genericattrib(id,root_genattrib_id,attrname,datatype,strval,unit,cityobject_id)
               VALUES({},{},'{}',1,'{}','kWh/m2a',{})'''.format(row[-1],row[-1],row[-2],row[2],row[1])
    cursor.execute(query)
    connection.commit()
    
def energy_class(scenario,cursor,class_rules,connection):
    
    # get yearly energy demand values in kWh/a for scenario
    query = '''select co.gmlid,gen.realval*1000,co.id as demand from cdb.cityobject as co
               join cdb.cityobject_genericattrib as gen
               on co.id = gen.cityobject_id
               where co.objectclass_id = 50033
               and gen.attrname LIKE '{}%' 
               and co.name LIKE '{}%' '''.format(scenario,scenario)
    cursor.execute(query)
    energyDem = cursor.fetchall()
    
    # get buildings + attributes gmlid,storeys_above_ground
    query = '''select cb.gmlid as co_gmlid,bldg.storeys_above_ground,ST_Area(sg.geometry) as area 
               from cityobject co join thematic_surface ts on co.id = ts.id
               join building bldg on building_id = bldg.id join surface_geometry sg
               on ts.id = sg.cityobject_id join cityobject cb on ts.building_id = cb.id
               where co.gmlid like 'Ground%' and sg.geometry is not null'''
    cursor.execute(query)
    bldg = cursor.fetchall()
   
    energyDemand = {}
    buildings = {}
    for obj in energyDem:
        energyDemand[obj[0]] = [obj[1],obj[2]]
    for obj in bldg:
        buildings[obj[0]] = [int(obj[1]),obj[2]]
    
    # normalise energy demand 
    for key1 in list(energyDemand.keys()):
        for key2 in list(buildings.keys()):
            if key2 in key1:
                energyDemand[key1][0] = energyDemand[key1][0]/(buildings[key2][0]*0.75*buildings[key2][1])
    
    # perform energy classification
    for key in list(energyDemand.keys()):
        for rule in class_rules:
            if energyDemand[key][0] >= class_rules[rule][0] and energyDemand[key][0] < class_rules[rule][1]:
                energyDemand[key].append(rule)
    
    # get id of last inserted row in cityobject_genericattrib
    query = '''select max(id) from cityobject_genericattrib'''
    cursor.execute(query)
    maxGenattribId = cursor.fetchone()[0] + 1
    
    # create + insert generic attribute
    for genattrib in energyDemand:
        energyDemand[genattrib].append('energy_label_'+scenario)
        energyDemand[genattrib].append(maxGenattribId)
        insert_genericattrib(cursor,energyDemand[genattrib],connection)
                
        maxGenattribId += 1
        
def main():
    
    # db connection 
    connection = psycopg2.connect(user='',
                                  password='',
                                  host='',
                                  port=,
                                  database='',
                                  options="")
    cursor = connection.cursor()
    scenarios = {'statusQuo': [],'mediumRefurb': [],'advRefurb': []}
    
    server = psycopg2.connect(user='',
                              password='',
                              host='',
                              port=,
                              database='',
                              options="")
    library = server.cursor()
    
    # clean energy labels from cityobject_genericattrib
    print('Cleaning energy label generic attributes...')
    query = '''delete from cdb.cityobject_genericattrib gen
               where gen.attrname like 'energy_label%' '''
    cursor.execute(query)
    connection.commit()
    
    # get classificatio rules from library database
    print('Pulling energy classification rules from libraryDB...')
    query = '''select label,value_from,value_to from energy_class where function = 'Residential' '''
    library.execute(query)
    class_rules = library.fetchall()
       
    rules = {}
    for row in class_rules:
        rules[row[0]] = [row[1],row[2]]
        
    # get energy demand values for each building for each scenario
    for scenario in scenarios:
        scenarios[scenario] = getEnergyDemand(cursor, scenario)
    
    # biggest decrease, monthly demand, demand by volume limit 10
    print('Finding buldings with biggest diff from scenario to scenario...')
    energyDifference(scenarios)
    bldgMonthlyGraph(cursor)
    print('Finding buildings with biggest volume')
    volDemandGraph(cursor,list(scenarios.keys()))
    
    # perform classification
    for scenario in scenarios:
        print('Classifying building performance for {}'.format(scenario))
        energy_class(scenario,cursor,rules,connection)
    
    
    # number of buildings in scenario
    for scenario in scenarios:
        query = '''select count(gen.id) num_buildings,gen.strval energy_class 
    				   from cdb.cityobject_genericattrib gen
    				   where gen.attrname like '%{}'
    				   group by gen.strval'''.format(scenario)
        cursor.execute(query)
        energyclass = cursor.fetchall()
        
        # print energy labels counts
        
        print('Label\t\t{}'.format(scenario))
        for row in energyclass:
            print('{}\t\t\t\t{}'.format(row[1],row[0]))
        
 
    print('Done!')
 
    
 
    
 
    
 
    

if __name__ == '__main__':
    main()
