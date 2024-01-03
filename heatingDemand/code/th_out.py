# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 19:20:18 2022

@author: TM
"""

import os
import uuid
import psycopg2

def getId(big_str):
    ob = '('
    cb = ')'
    idx1 = big_str.index(ob)
    idx2 = big_str.index(cb)
     
    return big_str[idx1+1:idx2]
    
def qs_from_thout(file):
    
    with open(file,'r') as th:
        simData = th.readlines()
        
        for i in range(len(simData)):
            simData[i] = simData[i].split('\t')
        
        i = 5
        heatingDemand = {}
        while i < len(simData[0]):
            # get index of energy demand and gml_id from **Qs(Wh)
            assert simData[0][i].endswith('Qs(Wh)')
            gmlId = getId(simData[0][i])
            assert len(gmlId) == 30
            
            # use index to get series and replace negatives with zero
            # create array to contain hourly, monthly and yearly time series for each energy deman object
            # monthly and yearly values populated later
            heatingDemand[gmlId] = [[]]
            for j in range(1,len(simData)):
                try:
                    assert float(simData[j][i]) > 0
                    heatingDemand[gmlId][0].append(float(simData[j][i]))
                except:
                    heatingDemand[gmlId][0].append(0)
                
            i += 13
        
        return heatingDemand

def series_monthly(buildings_hourly):
    
    for obj in buildings_hourly:
        monthly = []
        val = 0
        for i in range(12):
            month = 0
            hr = 0
            
            if i == 0:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 1:
                for j in range(28):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 2:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
               
            
            if i == 3:
                for j in range(30):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 4:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 5:
                for j in range(30):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 6:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 7:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 8:
                for j in range(30):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
            
            if i == 9:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
                
            if i == 10:
                for j in range(30):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
                
                
            if i == 11:
                for j in range(31):
                    while hr < 24:
                        month += buildings_hourly[obj][0][val]
                        val += 1
                        hr += 1 
                    if hr-1 == 23:
                        hr = 0
                monthly.append(round(month/1000,2))
        
        buildings_hourly[obj].append(monthly)
        
    return buildings_hourly

def series_yearly(buildings_monthly):
    
    for obj in buildings_monthly:
        buildings_monthly[obj].append(round(sum(buildings_monthly[obj][0])/1000000,2))
    
    return buildings_monthly

def add_units(buildings_yearly):
    
    for obj in buildings_yearly:
        buildings_yearly[obj].append(['Wh','kWh/month','MWh/a'])
        
    return buildings_yearly

def gmlid(objects):
    
    d = {}
    for obj in objects:
        new_id = 'HeatingDemand_' + obj + '_' + uuid.uuid4().hex.lower()[0:32]
        d[new_id] = objects[obj]
    return d

def cleanup(connection,cursor):
    
    queries = ['''delete from ng_cityobject''','''delete from ng_energydemand''',
               '''delete from ng_regulartimeseries''','''delete from ng_timeseries''',
               '''delete from cityobject_genericattrib where attrname like '%_heating_demand_citysim' ''',
               '''delete from cityobject_genericattrib where attrname like 'energy_label%' ''',
               '''delete from cityobject where objectclass_id = 50033''',
               '''delete from cityobject where objectclass_id = 50006'''
               ]
    for query in queries:
        cursor.execute(query)
        connection.commit()

def objectclassid(cursor,objectclass):

    # get objectclass_id of EnergyDemand 
    getClassId = '''select id from objectclass
                    where classname = '{}'
                 '''.format(objectclass)
    cursor.execute(getClassId)
    objectclass_id = cursor.fetchall()[0][0]    
    return objectclass_id
   
def ng_cityobject(objects,obj,idx):
    
    objects[obj][4][0]['db']['ngcityobject'] = idx
    return objects
    
def energydemand(objects,obj):
    
    objects[obj][4][0]['db']['energydemand'].append(objects[obj][4][0]['db']['energy_cityobject'][0])
    objects[obj][4][0]['db']['energydemand'].append(objects[obj][4][0]['db']['ngcityobject'])
    objects[obj][4][0]['db']['energydemand'].append('spaceHeating')
    objects[obj][4][0]['db']['energydemand'].append(objects[obj][4][0]['db']['timeseries'][0])
    objects[obj][4][0]['db']['energydemand'].append('Natural Gas')
    objects[obj][4][0]['db']['energydemand'].append('http://')
    
    return objects

def name(objects,obj,scenario,time):
    
    name = scenario + '_heating_demand_' + time
    objects[obj].append(name)
    
    return objects

def getEnvelope(obj,cursor):
    
    gml_id = obj[14:44]
    getEnv = (''' select envelope 
                from cdb.cityobject 
                where cityobject.gmlid = '{}'
                 '''.format(gml_id))
    cursor.execute(getEnv)
    env = cursor.fetchall()[0][0]
            
    return env

def energy_cityobject(objects,obj,idx,cursor):
    
    objects[obj][4][0]['db']['energy_cityobject'].append(idx)
    objects[obj][4][0]['db']['energy_cityobject'].append(50006)
    objects[obj][4][0]['db']['energy_cityobject'].append(obj)
    objects[obj][4][0]['db']['energy_cityobject'].append(objects[obj][-1])
    objects[obj][4][0]['db']['energy_cityobject'].append(getEnvelope(obj, cursor))
        
    return objects    

def series_cityobject(objects,obj,idx,cursor):

    objects[obj][4][0]['db']['series_cityobject'].append(idx)
    objects[obj][4][0]['db']['series_cityobject'].append(50033)
    objects[obj][4][0]['db']['series_cityobject'].append(obj)
    objects[obj][4][0]['db']['series_cityobject'].append(objects[obj][-1])
    objects[obj][4][0]['db']['series_cityobject'].append(getEnvelope(obj, cursor))
        
    return objects 
        
def ng_time_series(objects,obj,idx,cursor):
    
    objects[obj][4][0]['db']['timeseries'].append(objects[obj][4][0]['db']['series_cityobject'][0])
    objects[obj][4][0]['db']['timeseries'].append(50033)
    objects[obj][4][0]['db']['timeseries'].append('estimation')
    objects[obj][4][0]['db']['timeseries'].append('averageInSucceedingInterval')
    objects[obj][4][0]['db']['timeseries'].append('Quality description text')
    objects[obj][4][0]['db']['timeseries'].append('Source text')
       
    return objects

def ng_reg_timeseries(objects,obj,time_interval,time_interval_unit,data_idx):
    
    objects[obj][4][0]['db']['regulartimeseries'].append(objects[obj][4][0]['db']['timeseries'][0])
    objects[obj][4][0]['db']['regulartimeseries'].append(time_interval)
    objects[obj][4][0]['db']['regulartimeseries'].append(time_interval_unit)
    objects[obj][4][0]['db']['regulartimeseries'].append(objects[obj][data_idx])
    objects[obj][4][0]['db']['regulartimeseries'].append(objects[obj][3][data_idx])
        
    return objects

def generic_attrib(objects,obj,name,idx):
    
    objects[obj][4][0]['db']['generic'].append(idx)
    objects[obj][4][0]['db']['generic'].append(idx)
    objects[obj][4][0]['db']['generic'].append(name+'_heating_demand_citysim')
    objects[obj][4][0]['db']['generic'].append(6)
    objects[obj][4][0]['db']['generic'].append(objects[obj][2])
    objects[obj][4][0]['db']['generic'].append(objects[obj][3][2])
    objects[obj][4][0]['db']['generic'].append(objects[obj][4][0]['db']['series_cityobject'][0])
        
    return objects

def list_to_series(objects,obj):
    values = ''
    for val in objects[obj][4][0]['db']['regulartimeseries'][3]:
        values += str(val)
        values += ' '
    objects[obj][4][0]['db']['regulartimeseries'][3] = values
   
    return objects

def insert_ng_cityobject(obj,connection,cursor):
    
    query = '''insert into ng_cityobject(id)
                      values({})'''.format(obj[4][0]['db']['ngcityobject'])
    
    cursor.execute(query)
    connection.commit()

def insert_seriesobject(obj,connection,cursor):
    
    query = '''INSERT INTO cityobject(id,objectclass_id,gmlid,name,envelope)
               VALUES({},{},'{}','{}','{}')'''.format(obj[4][0]['db']['series_cityobject'][0],
                                                    obj[4][0]['db']['series_cityobject'][1],
                                                    obj[4][0]['db']['series_cityobject'][2],
                                                    obj[4][0]['db']['series_cityobject'][3],
                                                    obj[4][0]['db']['series_cityobject'][4])
    
    cursor.execute(query)
    connection.commit()                                                
    
def insert_ng_timeseries(obj,connection,cursor):
    
    query = '''INSERT INTO ng_timeseries(id,objectclass_id,timevaluesprop_acquisitionme,timevaluesprop_interpolation,timevaluesprop_qualitydescri,timevaluespropertiest_source)
               VALUES({},{},'{}','{}','{}','{}')'''.format(obj[4][0]['db']['timeseries'][0],
                                                      obj[4][0]['db']['timeseries'][1],
                                                      obj[4][0]['db']['timeseries'][2],
                                                      obj[4][0]['db']['timeseries'][3],
                                                      obj[4][0]['db']['timeseries'][4],
                                                      obj[4][0]['db']['timeseries'][5]
                                                      )
    
    
    cursor.execute(query)
    connection.commit()

def insert_energyobject(obj,connection,cursor):
    
    query = '''INSERT INTO cityobject(id,objectclass_id,gmlid,name,envelope)
               VALUES({},{},'{}','{}','{}')'''.format(obj[4][0]['db']['energy_cityobject'][0],
                                                    obj[4][0]['db']['energy_cityobject'][1],
                                                    obj[4][0]['db']['energy_cityobject'][2],
                                                    obj[4][0]['db']['energy_cityobject'][3],
                                                    obj[4][0]['db']['energy_cityobject'][4])
    
    cursor.execute(query)
    connection.commit()
                      
def insert_ng_energydemand(obj,connection,cursor):
        
    query = '''insert into ng_energydemand(id,cityobject_demands_id,enduse,energyamount_id,energycarriertype,energycarriertype_codespace)
               values({},{},'{}',{},'{}','{}')'''.format(obj[4][0]['db']['energydemand'][0],
                                                   obj[4][0]['db']['energydemand'][1],
                                                   obj[4][0]['db']['energydemand'][2],
                                                   obj[4][0]['db']['energydemand'][3],
                                                   obj[4][0]['db']['energydemand'][4],
                                                   obj[4][0]['db']['energydemand'][5]
                                                   )
    
    cursor.execute(query)
    connection.commit()                     

def insert_ng_regulartimeseries(obj,connection,cursor,time_interval):
    
    if time_interval == 'year':
        query = '''INSERT INTO ng_regulartimeseries(id,timeinterval,timeinterval_unit,values_,values_uom)
                   VALUES({},{},'{}',{},'{}')'''.format(obj[4][0]['db']['regulartimeseries'][0],
                                                          obj[4][0]['db']['regulartimeseries'][1],
                                                          obj[4][0]['db']['regulartimeseries'][2],
                                                          obj[4][0]['db']['regulartimeseries'][3],
                                                          obj[4][0]['db']['regulartimeseries'][4],
                                                          )
        
        cursor.execute(query)
        connection.commit()
    else:
        query = '''INSERT INTO ng_regulartimeseries(id,timeinterval,timeinterval_unit,values_,values_uom)
                   VALUES({},{},'{}','{}','{}')'''.format(obj[4][0]['db']['regulartimeseries'][0],
                                                          obj[4][0]['db']['regulartimeseries'][1],
                                                          obj[4][0]['db']['regulartimeseries'][2],
                                                          obj[4][0]['db']['regulartimeseries'][3],
                                                          obj[4][0]['db']['regulartimeseries'][4],
                                                          )
        
        cursor.execute(query)
        connection.commit()
   
def insert_genericattrib(obj,connection,cursor):
    
    query = '''INSERT INTO cityobject_genericattrib(id,root_genattrib_id,attrname,datatype,realval,unit,cityobject_id)
               VALUES({},{},'{}',{},{},'{}',{})'''.format(obj[4][0]['db']['generic'][0],
                                                          obj[4][0]['db']['generic'][1],
                                                          obj[4][0]['db']['generic'][2],
                                                          obj[4][0]['db']['generic'][3],
                                                          obj[4][0]['db']['generic'][4],
                                                          obj[4][0]['db']['generic'][5],
                                                          obj[4][0]['db']['generic'][6],
                                                          )
    
    
    cursor.execute(query)
    connection.commit()
    
def insertDb(objects,connection,cursor,time_interval):
        
    for obj in objects:
        insert_ng_cityobject(objects[obj],connection,cursor)
        insert_seriesobject(objects[obj], connection, cursor)
        insert_ng_timeseries(objects[obj], connection, cursor)
        insert_energyobject(objects[obj],connection,cursor)
        insert_ng_energydemand(objects[obj], connection, cursor)
        insert_ng_regulartimeseries(objects[obj], connection, cursor,time_interval)
        if time_interval == 'year':
            insert_genericattrib(objects[obj], connection, cursor)
        
def max_id(cursor,query):
    
    cursor.execute(query)
    maxId = (cursor.fetchall()[0][0])
    if maxId == None:
        return 1
    else:
        return maxId
 
def main():
    
    os.chdir('../data')
    
    # db connection 
    connection = psycopg2.connect(user='',
                                  password='',
                                  host='',
                                  port=,
                                  database='',
                                  options="")
    cursor = connection.cursor()
    
    # cleanup relevant EnergyADE tables
    cleanup(connection,cursor)
    
    # get max(id) for objects
    maxngCityobjectId = max_id(cursor, '''select max(id) from ng_cityobject''')
    maxCityobjectId = max_id(cursor, '''select max(id) from cityobject''')
    maxngEnergydemandId = max_id(cursor, '''select max(id) from ng_energydemand''')
    maxGenattribId = max_id(cursor, '''select max(id) from cityobject_genericattrib''')
    ade_objects = ''
    
    # for each scenario, get Qs(Wh) and create energy demand objects + add generic attributes
    for file in os.listdir():
        if file.endswith('TH.out'):
            
            scenario = file[17:-7]
            print('\nFile: {}'.format(file))
            print('Scenario: {}'.format(scenario))
            print('Getting data from file...')
            
            # time series + units
            heatingDemand = qs_from_thout(file)
            heatingDemandMonthly = series_monthly(heatingDemand)
            heatingDemandYearly = series_yearly(heatingDemandMonthly)
            heatingDemandUnits = add_units(heatingDemandYearly)
            
           
            # new gml:id
            print('Modifying gmlid...')
            ade_objects = gmlid(heatingDemandUnits)
            for key in list(ade_objects.keys()):
                ade_objects[key].append(0)
            
            intervals = {'year': [1,'yearly'], 'month': [0.0833, 'monthly'], 'hour': [1, 'hourly']}
            data = 2
            print('Creating objects...')
            for interval in intervals:
                print('Interval: {}'.format(interval))
                
                # dict() containers for table data
                # for each energy demand object:
                    # create relevant ade objects and cityobjects
                    #insert into database
                for obj in ade_objects:
                    
                    maxCityobjectId += 1
                    maxngCityobjectId += 1
                    maxngEnergydemandId += 1
                    
                    ade_objects[obj][4] = [{'db':
                                              {'ngcityobject': 0,
                                               'energydemand': [],
                                               'energy_cityobject': [],
                                               'series_cityobject': [],
                                               'timeseries': [],
                                               'regulartimeseries': [],
                                               'generic':[]}
                                              }]
                    ade_objects = ng_cityobject(ade_objects,obj,maxngCityobjectId)
                    ade_objects = name(ade_objects,obj,scenario,intervals[interval][1])
                    ade_objects = energy_cityobject(ade_objects,obj,maxCityobjectId,cursor)
                    maxCityobjectId += 1
                    ade_objects = series_cityobject(ade_objects,obj,maxCityobjectId,cursor)
                    ade_objects = ng_time_series(ade_objects,obj,maxCityobjectId,cursor)
                    ade_objects = energydemand(ade_objects,obj)
                    ade_objects = ng_reg_timeseries(ade_objects,obj,intervals[interval][0],interval,data)
                    
                    if interval == 'year':
                        maxGenattribId += 1
                        ade_objects = generic_attrib(ade_objects,obj,scenario,maxGenattribId)
                    
                    if interval == 'month' or interval == 'hour':
                        ade_objects = list_to_series(ade_objects,obj)
                print('Inserting into database...')  
                insertDb(ade_objects,connection,cursor,interval)
                data -= 1
    print('Done!')
    
    # get number of energydemand objects and ade-cityobject_genericattributes
    num_energydemand_objects = '''select count(*) from cdb.ng_energydemand'''
    cursor.execute(num_energydemand_objects)
    num_energydemand_objects = cursor.fetchall()[0][0]
    num_genericattrub = '''select count(*) from cdb.cityobject_genericattrib
                           join cdb.cityobject
                           on cdb.cityobject_genericattrib.cityobject_id = cdb.cityobject.id
                           where cdb.cityobject.objectclass_id = 50033
                           or cdb.cityobject.objectclass_id = 50006'''
    cursor.execute(num_genericattrub)
    num_genericattrub = cursor.fetchall()[0][0]
    print('Number of generic attributes: {}'.format(num_genericattrub))
    print('Number of EnergyDemand objects: {}'.format(num_energydemand_objects))
    
    

if __name__ == '__main__':
    main()
    

            
            
            
        
     