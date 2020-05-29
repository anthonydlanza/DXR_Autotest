import BAC0
from time import sleep
import csv
import pandas as pd
import numpy as np

dxr_name = []
dxr_addresses = []
dxr_instance = []
dxr_damper = []
dxr_valve = []
dxr_temp = []

# construct your dataframe for performance analytics

df = pd.DataFrame([['Sample','0.0.0.0',0,0,0,0,0,0,0,0,0,0,0,0,0,'NaN']],
    index = [0],
    columns = [
    'VAV',
    'IP Address',
    'Max Cool Stpt',
    'Cooling Air Volume',
    'Cooling Damper Pos',
    'Cooling Valve Pos',
    'Discharge Air Temperature @ 0%',
    'Max Heat Stpt',
    'Heating Air Volume',
    'Heating Damper Pos',
    'Heating Heating Valve Pos',
    'Discharge Air Temperature @ 100%',
    'Air Vol Dif Cool/Heat',
    'Damper Dif Cool/Heat',
    'Discharge Temp Dif Cool/Heat',
    'comments'])

# set up a dictionary to relate states to their enumerated value

states = {'Initial':1,'Balancg':2,'Balancd':3}
modes = {'MxCool':1,'MxHeat':2}

# get computer's IP address

myIp = input("Your Ip address: ")

# create an instance of BAC0

bacnet = BAC0.connect(ip=myIp)

# run tests on boxes listed in boxes.csv
with open("boxes.csv",'r') as f:
    boxes = csv.reader(f)
    for row in boxes:
        # initialize performance arrays for cooling and heating tests

        cooling = dict(air_vol_stpt=0,air_volume=0,damper_pos=0,supply_temp=0,valve_pos=0)
        heating = dict(air_vol_stpt=0,air_volume=0,damper_pos=0,supply_temp=0,valve_pos=0)
        damper_command_present = False
        valve_command_present = False
        supply_temp_present = False
        air_stpt_present = False
        air_volume_present = False
        comments = ""

        # connect to the dxr
        try:
	        dxr = BAC0.device(row[1],row[2],bacnet)

	        # read the objectList

	        dxr_objlist = row[1] + " device " + row[2] + " objectList"
	        points = bacnet.read(dxr_objlist)

	        # points = bacnet.read('10.73.4.55 device 700015 objectList')

	        # list points by name as key/value pairs
	        # additionally, find the long string that contains floor and segment info
	        # -- we will use this to identify the name of VavSuBalSta
	        
	        point_strings = []
	        for point in dxr.points:
	            # print(point)
	            point_strings.append(str(point))

	        for point in point_strings:
	            print(point)
	            if row[3] in point:
	                damper_command_present = True
	            if row[4] in point:
	                valve_command_present = True
	            if row[5] in point:
	                supply_temp_present = True
	            if row[6] in point:
	                air_stpt_present = True
	            if row[7] in point:
	                air_volume_present = True
	        matching = [sta for sta in point_strings if 'VavSuBalSta' in sta]
	        long_name = str(matching[0])[len(row[0])+1:-21]
	        print(long_name)
	        balancing_state_name = long_name + 'VavSuBalSta'
	        balancing_mode_name = long_name + 'VavSuBalMod'
	        print(balancing_state_name)
	        print(balancing_mode_name)

	        # release operator priority from Damper and Heating Valve

	        if damper_command_present == True:
	            dxr[str(row[3])] = 'auto'
	        else:
	            print("This DXR doesn't appear to have to have the DAMPER POS # you specified.")
	        if valve_command_present == True:
	            dxr[str(row[4])] = 'auto'
	        else:
	            print("This DXR doesn't appear to have to have the HTG VLV POS # you specified.")

	        # Pre-test Balancing state of the unit

	        balancing_state = dxr[balancing_state_name]
	        state = str(balancing_state)[-7:]

	        # Command the unit into Cooling

	        for i in range(0,5):
	            print("-*-"*10)
	        print("Running Cooling test")
	        dxr[balancing_state_name] = states['Balancg']
	        dxr[balancing_mode_name] = modes['MxCool']
	        if valve_command_present == True:
	            dxr[str(row[4])] = 0

	        # record values for cooling test

	        sleep(60)
	        if air_stpt_present == True:
	            cooling['air_vol_stpt'] = str(dxr[str(row[6])])
	        else:
	            cooling['air_vol_stpt'] = row[0] + row[6] + "    0.00 cubicFeetPerMinute"
	        if air_volume_present == True:
	            cooling['air_volume'] = str(dxr[str(row[7])])
	        else:
	            cooling['air_volume'] = row[0] + row[7] + "    0.00 cubicFeetPerMinute"
	        if damper_command_present == True:
	            cooling['damper_pos'] = str(dxr[str(row[3])])
	        else:
	            cooling['damper_pos'] = row[0] + row[3] + "    0.00 percent"
	        if supply_temp_present == True:
	            cooling['supply_temp'] = str(dxr[str(row[5])])
	        else:
	            cooling['supply_temp'] = row[0] + row[5] + "    0.00 degreesFahrenheit"
	        if valve_command_present == True:
	            cooling['valve_pos'] = str(dxr[str(row[4])])
	        else:
	            cooling['valve_pos'] = row[0] + row[4] + "    0.00 percent"

	        # command the unit into Max Heating

	        for i in range(0,5):
	            print("-*-"*10)
	        print("Running heating test")
	        dxr[balancing_state_name] = states['Balancg']
	        dxr[balancing_mode_name] = modes['MxHeat']
	        if valve_command_present == True:
	            dxr[str(row[4])] = 100

	        # record values for heating test

	        sleep(60)
	        if air_stpt_present == True:
	            heating['air_vol_stpt'] = str(dxr[str(row[6])])
	        else:              
	            heating['air_vol_stpt'] = row[0] + row[6] + "    0.00 cubicFeetPerMinute"
	            comments = comments + "This DXR doesn't appear to have to have the AIR VOL SP # you specified. "
	        if air_volume_present == True:
	            heating['air_volume'] = str(dxr[str(row[7])])
	        else:
	            heating['air_volume'] = row[0] + row[7] + "    0.00 cubicFeetPerMinute"
	            comments = comments + "This DXR doesn't appear to have to have the AIR VOLUME # you specified. "
	        if damper_command_present == True:
	            heating['damper_pos'] = str(dxr[str(row[3])])
	        else:
	            heating['damper_pos'] = row[0] + row[3] + "    0.00 percent"
	            comments = comments + "This DXR doesn't appear to have to have the DAMPER POS # you specified. "
	        if supply_temp_present == True:
	            heating['supply_temp'] = str(dxr[str(row[5])])
	        else:
	            heating['supply_temp'] = row[0] + row[5] + "    0.00 degreesFahrenheit"
	            comments = comments + "This DXR doesn't appear to have to have the SPLY TEMP # you specified. "
	        if valve_command_present == True:
	            heating['valve_pos'] = str(dxr[str(row[4])])
	        else:
	            heating['valve_pos'] = row[0] + row[4] + "    0.00 percent"
	            comments = comments + "This DXR doesn't appear to have to have the HTG VLV POS # you specified. "

	        # place the unit back to it's pre-test balancing state

	        dxr["SantaMonicaServices'Flr_01'RSegm_84'HVAC'VavSu'VavSuBalSta"] = states[state]

	        # release the heating valve

	        if valve_command_present == True:
	            dxr[str(row[4])] = 'auto'

	        # convert strings to integer values & calculate differentials

	        #

	        if cooling['air_volume'] == 'None':
	               cooling['air_volume'] = row[0] + row[7] + "    0.00 cubicFeetPerMinute"
	               heating['air_volume'] = row[0] + row[7] + "    0.00 cubicFeetPerMinute"

	        cooling_cfm_float = float(str(cooling['air_volume'])[len(row[0]) + len(row[7]) + 4:-19:])
	        heating_cfm_float = float(str(heating['air_volume'])[len(row[0]) + len(row[7]) + 4:-19:])
	        air_vol_dif = int(cooling_cfm_float - heating_cfm_float)

	        if int(cooling_cfm_float) == 0 and int(heating_cfm_float) == 0:
	            comments = comments + "Airflow sensor failed. "
	        elif air_vol_dif < -10:
	            comments = comments + "Damper may be reversed. "
	        elif air_vol_dif > -10 and air_vol_dif < 10:
	            comments = comments + "If box is not a CAV, damper may be slipped on shaft. "

	        if cooling['damper_pos'] == 'None':
	           cooling['damper_pos'] = row[0] + row[3] + "    0.00 percent"
	           heating['damper_pos'] = row[0] + row[3] + "    0.00 percent"

	        cooling_dmpr_float = float(str(cooling['damper_pos'])[len(row[0]) + len(row[3]) + 4:-8:])
	        heating_dmpr_float = float(str(heating['damper_pos'])[len(row[0]) + len(row[3]) + 4:-8:])
	        dmpr_dif = int(cooling_dmpr_float - heating_dmpr_float)

	        if dmpr_dif < 0:
	            comments = comments + "Check air vol stpts. "

	        if cooling['supply_temp'] == 'None':
	               cooling['supply_temp'] = row[0] + row[5] + "    0.00 degreesFahrenheit"
	               heating['supply_temp'] = row[0] + row[5] + "    0.00 degreesFahrenheit"
	           
	        cooling_temp_float = float(str(cooling['supply_temp'])[len(row[0]) + len(row[5]) + 4:-18:])
	        heating_temp_float = float(str(heating['supply_temp'])[len(row[0]) + len(row[5]) + 4:-18:])        
	        temp_dif = int(cooling_temp_float - heating_temp_float)

	        if int(cooling_temp_float) == 0 and int(heating_temp_float) == 0:
	            comments = comments + "Temp sensor failed. "
	        elif temp_dif < -5:
	            comments = comments + "Check valve direction."
	        elif temp_dif >= -5 and temp_dif < 10:
	            comments = comments + "Valve may be stuck or isolation valve may be closed."

	        # write data to dataframe

	        df = df.append(
	            {'VAV':row[0],
	            'IP Address':row[1],
	            'Max Cool Stpt':str(dxr['CLG FLOW MAX'])[len(row[0]) + len(row[6]) + 4:],
	            'Cooling Air Volume':str(cooling['air_volume'])[len(row[0]) + len(row[7]) + 4:],
	            'Cooling Damper Pos':str(cooling['damper_pos'])[len(row[0]) + len(row[3]) + 4:],
	            'Cooling Valve Pos':str(cooling['valve_pos'])[len(row[0]) + len(row[4]) + 4:],
	            'Discharge Air Temperature @ 0%':str(cooling['supply_temp'])[len(row[0]) + len(row[5]) + 4:],
	            'Max Heat Stpt':str(dxr['HTG FLOW MAX'])[len(row[0]) + len(row[6]) + 4:],
	            'Heating Air Volume':str(heating['air_volume'])[len(row[0]) + len(row[7]) + 4:],
	            'Heating Damper Pos':str(heating['damper_pos'])[len(row[0]) + len(row[3]) + 4:],
	            'Heating Heating Valve Pos':str(heating['valve_pos'])[len(row[0]) + len(row[4]) + 4:],
	            'Discharge Air Temperature @ 100%':str(heating['supply_temp'])[len(row[0]) + len(row[5]) + 4:],
	            'Air Vol Dif Cool/Heat':str(air_vol_dif) + " cubicFeetPerMinute",
	            'Damper Dif Cool/Heat':str(dmpr_dif) + " percent",
	            'Discharge Temp Dif Cool/Heat':str(temp_dif) + " degreesFahrenheit",
	            'comments':str(comments)
	            }, ignore_index=True)
        except:
            df = df.append(
	            {'VAV':row[0],
	            'IP Address':row[1],
	            'Max Cool Stpt':'Nan',
	            'Cooling Air Volume':'Nan',
	            'Cooling Damper Pos':'Nan',
	            'Cooling Valve Pos':'Nan',
	            'Discharge Air Temperature @ 0%':'Nan',
	            'Max Heat Stpt':'Nan',
	            'Heating Air Volume':'Nan',
	            'Heating Damper Pos':'Nan',
	            'Heating Heating Valve Pos':'Nan',
	            'Discharge Air Temperature @ 100%':'Nan',
	            'Air Vol Dif Cool/Heat':'Nan',
	            'Damper Dif Cool/Heat':'Nan',
	            'Discharge Temp Dif Cool/Heat':'Nan',
	            'comments':"Could not connect to DXR. "
	            }, ignore_index=True)
            pass
df.to_csv('SystemPerformance.csv')
