from odoo import api, fields, models, _, tools
from odoo.osv import expression
import base64
from odoo import modules
from odoo.exceptions import AccessError, UserError, ValidationError
from PIL import Image




class vehicel_assessment(models.Model):
    _name = 'vehicle.assessment'

    selection_body = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
    ]

    selection_engine = [
        ('complete', 'complete'),
        ('un-complete', 'uncomplete'),
        ('leakage', 'leakage'),
        ('non-leakage', 'non-leakage'),
        ('noise', 'noise'),
        ('no-noise', 'no-noise'),

        ('present', 'present'),
        ('not-present', 'not-present'),


        ('vibration', 'vibration'),
        ('non-vibrate', 'non-vibrate'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    selection_brakes = [
        ('smooth', 'smooth'),
        ('morethan50', 'more than 50%'),
        ('lessthan50', 'less than 50%'),

        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    selection_suspension = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    selection_interior = [
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),

    ('working', 'working'),
        ('not-working', 'not-working'),
    ]

    selection_ac = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),

    ('working', 'working'),
        ('not-working', 'not-working'),
    ]

    selection_electrical = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('noise', 'noise'),
        ('no-noise', 'no-noise'),

        ('present', 'present'),
        ('not-present', 'not-present'),

        ('vibration', 'vibration'),
        ('non-vibrate', 'non-vibrate'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    selection_exterior = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('noise', 'noise'),
        ('no-noise', 'no-noise'),

        ('present', 'present'),
        ('not-present', 'not-present'),

        ('vibration', 'vibration'),
        ('non-vibrate', 'non-vibrate'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    selection_tyre = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('noise', 'noise'),
        ('no-noise', 'no-noise'),

        ('present', 'present'),
        ('not-present', 'not-present'),

        ('vibration', 'vibration'),
        ('non-vibrate', 'non-vibrate'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),

    ]
    selection_drive = [
        ('accident', 'accident'),
        ('non-accident', 'non-accident'),
        ('noise', 'noise'),
        ('no-noise', 'no-noise'),

        ('present', 'present'),
        ('not-present', 'not-present'),

        ('vibration', 'vibration'),
        ('non-vibrate', 'non-vibrate'),
        ('ok', 'ok'),
        ('not-ok', 'not-ok'),
    ]

    name = fields.Char('Name')
    vehicle = fields.Many2one('vehicle')

    Radiator_Core_Support = fields.Selection(selection_body,string="Radiator")
    Radiator_Core_Support_img= fields.Selection(selection_body,string="Radiator")

    Right_Strut_Tower_Apron= fields.Selection(selection_body,string="Radiator")
    Right_Strut_Tower_Apron_img= fields.Selection(selection_body,string="Radiator")

    Left_Strut_Tower_Apron= fields.Selection(selection_body,string="Radiator")
    Left_Strut_Tower_Apron_img= fields.Selection(selection_body,string="Radiator")

    Right_Front_Rail= fields.Selection(selection_body,string="Radiator")
    Right_Front_Rail_img= fields.Selection(selection_body,string="Radiator")

    Left_Front_Rail= fields.Selection(selection_body,string="Radiator")
    Left_Front_Rail_img= fields.Selection(selection_body,string="Radiator")

    Cowl_Panel_Firewall= fields.Selection(selection_body,string="Radiator")
    Cowl_Panel_Firewall_img= fields.Selection(selection_body,string="Radiator")

    RightA_Pillar= fields.Selection(selection_body,string="Radiator")
    RightA_Pillar_img= fields.Selection(selection_body,string="Radiator")

    LeftA_Pillar= fields.Selection(selection_body,string="Radiator")
    LeftA_Pillar_img= fields.Selection(selection_body,string="Radiator")

    RightB_Pillar= fields.Selection(selection_body,string="Radiator")
    RightB_Pillar_img= fields.Selection(selection_body,string="Radiator")

    LeftB_Pillar= fields.Selection(selection_body,string="Radiator")
    LeftB_Pillar_img= fields.Selection(selection_body,string="Radiator")

    RightC_Pillar= fields.Selection(selection_body,string="Radiator")
    RightC_Pillar_img= fields.Selection(selection_body,string="Radiator")

    LeftC_Pillar= fields.Selection(selection_body,string="Radiator")
    LeftC_Pillar_img= fields.Selection(selection_body,string="Radiator")

    Boot_Floor= fields.Selection(selection_body,string="Radiator")
    Boot_Floor_img= fields.Selection(selection_body,string="Radiator")

    Boot_Lock_Pillar= fields.Selection(selection_body,string="Radiator")
    Boot_Lock_Pillar_img= fields.Selection(selection_body,string="Radiator")

    Front_Sub_Frame= fields.Selection(selection_body,string="Radiator")
    Front_Sub_Frame_img= fields.Selection(selection_body,string="Radiator")

    Rear_Sub_Frame= fields.Selection(selection_body,string="Radiator")
    Rear_Sub_Frame_img= fields.Selection(selection_body,string="Radiator")

    # ---------------------------------------------------------------

    Engine_Oil_Level= fields.Selection(selection_engine,string="Radiator")
    Engine_Oil_Level_img= fields.Selection(selection_engine,string="Radiator")

    Engine_Oil_Leakage= fields.Selection(selection_engine,string="Radiator")
    Engine_Oil_Leakage_img= fields.Selection(selection_engine,string="Radiator")

    Transmission_Oil_Leakage= fields.Selection(selection_engine,string="Radiator")
    Transmission_Oil_Leakage_img= fields.Selection(selection_engine,string="Radiator")

    Brake_Oil_Level= fields.Selection(selection_engine,string="Radiator")
    Brake_Oil_Level_img= fields.Selection(selection_engine,string="Radiator")

    Brake_Oil_Leakage= fields.Selection(selection_engine,string="Radiator")
    Brake_Oil_Leakage_img= fields.Selection(selection_engine,string="Radiator")

    Washer_Fluid_Level= fields.Selection(selection_engine,string="Radiator")
    Washer_Fluid_Level_img= fields.Selection(selection_engine,string="Radiator")

    Washer_Fluid_Leakage= fields.Selection(selection_engine,string="Radiator")
    Washer_Fluid_Leakage_img= fields.Selection(selection_engine,string="Radiator")

    Coolant_Leakage= fields.Selection(selection_engine,string="Radiator")
    Coolant_Leakage_img= fields.Selection(selection_engine,string="Radiator")

    Catalytic_Convertor= fields.Selection(selection_engine,string="Radiator")
    Catalytic_Convertor_img= fields.Selection(selection_engine,string="Radiator")

    Exhaust_Sound= fields.Selection(selection_engine,string="Radiator")
    Exhaust_Sound_img= fields.Selection(selection_engine,string="Radiator")

    Exhaust_Joints= fields.Selection(selection_engine,string="Radiator")
    Exhaust_Joints_img= fields.Selection(selection_engine,string="Radiator")

    Radiator= fields.Selection(selection_engine,string="Radiator")
    Radiator_img= fields.Selection(selection_engine,string="Radiator")

    Suction_Fan= fields.Selection(selection_engine,string="Radiator")
    Suction_Fan_img= fields.Selection(selection_engine,string="Radiator")

    Starter_Operation= fields.Selection(selection_engine,string="Radiator")
    Starter_Operation_img= fields.Selection(selection_engine,string="Radiator")

# brakes===============================================================

    Front_Right_Disc= fields.Selection(selection_brakes,string="Radiator")
    Front_Right_Disc_img= fields.Selection(selection_brakes,string="Radiator")

    Front_Left_Disc= fields.Selection(selection_brakes,string="Radiator")
    Front_Left_Disc_img= fields.Selection(selection_brakes,string="Radiator")

    Front_Right_Brake_Pad= fields.Selection(selection_brakes,string="Radiator")
    Front_Right_Brake_Pad_img= fields.Selection(selection_brakes,string="Radiator")

    Front_Left_Brake_Pad= fields.Selection(selection_brakes,string="Radiator")
    Front_Left_Brake_Pad_img= fields.Selection(selection_brakes,string="Radiator")

    Parking_Hand_Brake= fields.Selection(selection_brakes,string="Radiator")
    Parking_Hand_Brake_img= fields.Selection(selection_brakes,string="Radiator")

# Interior===============================================================

    Steering_Wheel_Condition= fields.Selection(selection_interior,string="Radiator")
    Steering_Wheel_Condition_img= fields.Selection(selection_interior,string="Radiator")

    Steering_Wheel_Buttons= fields.Selection(selection_interior,string="Radiator")
    Steering_Wheel_Buttons_img= fields.Selection(selection_interior,string="Radiator")

    Horn= fields.Selection(selection_interior,string="Radiator")
    Horn_img= fields.Selection(selection_interior,string="Radiator")

    Lights_Lever_Switch= fields.Selection(selection_interior,string="Radiator")
    Lights_Lever_Switch_img= fields.Selection(selection_interior,string="Radiator")

    Wiper_Washer_Lever= fields.Selection(selection_interior,string="Radiator")
    Wiper_Washer_Lever_img= fields.Selection(selection_interior,string="Radiator")


# AC heater===============================================================

    AC_Fitted= fields.Selection(selection_ac,string="Radiator")
    AC_Fitted_img= fields.Selection(selection_ac,string="Radiator")

    AC_Operational= fields.Selection(selection_ac,string="Radiator")
    AC_Operational_img= fields.Selection(selection_ac,string="Radiator")

    Blower_Condenser= fields.Selection(selection_ac,string="Radiator")
    Blower_Condenser_img= fields.Selection(selection_ac,string="Radiator")

    Compressor_Operatio= fields.Selection(selection_ac,string="Radiator")
    Compressor_Operatio_img= fields.Selection(selection_ac,string="Radiator")

    Cooling_Excellent= fields.Selection(selection_ac,string="Radiator")
    Cooling_Excellent_img= fields.Selection(selection_ac,string="Radiator")

    Heating= fields.Selection(selection_ac,string="Radiator")
    Heating_img= fields.Selection(selection_ac,string="Radiator")

# electial heater===============================================================

    Voltage= fields.Selection(selection_electrical,string="Radiator")
    Voltage_img= fields.Selection(selection_electrical,string="Radiator")

    Terminals_Condition= fields.Selection(selection_electrical,string="Radiator")
    Terminals_Condition_img= fields.Selection(selection_electrical,string="Radiator")

    Charging= fields.Selection(selection_electrical,string="Radiator")
    Charging_img= fields.Selection(selection_electrical,string="Radiator")

    Alternator_Operation= fields.Selection(selection_electrical,string="Radiator")
    Alternator_Operation_img= fields.Selection(selection_electrical,string="Radiator")

    Gauges= fields.Selection(selection_electrical,string="Radiator")
    Gauges_img= fields.Selection(selection_electrical,string="Radiator")



 # exterior---------------------------------------------

    Trunk_Lock= fields.Selection(selection_exterior,string="Radiator")
    Trunk_Lock_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Windshield_Condition= fields.Selection(selection_exterior,string="Radiator")
    Front_Windshield_Condition_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Windshield_Condition= fields.Selection(selection_exterior,string="Radiator")
    Rear_Windshield_Condition_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Right_Door_Fittings= fields.Selection(selection_exterior,string="Radiator")
    Front_Right_Door_Fittings_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Left_Door_Fittings= fields.Selection(selection_exterior,string="Radiator")
    Front_Left_Door_Fittings_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Right_Door_Fittings= fields.Selection(selection_exterior,string="Radiator")
    Rear_Right_Door_Fittings_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Left_Door_Fittings= fields.Selection(selection_exterior,string="Radiator")
    Rear_Left_Door_Fittings_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Right_Door_Levers= fields.Selection(selection_exterior,string="Radiator")
    Front_Right_Door_Levers_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Left_Door_Levers= fields.Selection(selection_exterior,string="Radiator")
    Front_Left_Door_Levers_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Right_Door_Levers= fields.Selection(selection_exterior,string="Radiator")
    Rear_Right_Door_Levers_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Left_Door_Levers= fields.Selection(selection_exterior,string="Radiator")
    Rear_Left_Door_Levers_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Right_Door_Window= fields.Selection(selection_exterior,string="Radiator")
    Front_Right_Door_Window_img= fields.Selection(selection_exterior,string="Radiator")

    Front_Left_Door_Window= fields.Selection(selection_exterior,string="Radiator")
    Front_Left_Door_Window_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Right_Door_Window= fields.Selection(selection_exterior,string="Radiator")
    Rear_Right_Door_Window_img= fields.Selection(selection_exterior,string="Radiator")

    Rear_Left_Door_Window= fields.Selection(selection_exterior,string="Radiator")
    Rear_Left_Door_Window_img= fields.Selection(selection_exterior,string="Radiator")

    Windscreen_Wiper= fields.Selection(selection_exterior,string="Radiator")
    Windscreen_Wiper_img= fields.Selection(selection_exterior,string="Radiator")

    Right_Headlight= fields.Selection(selection_exterior,string="Radiator")
    Right_Headlight_img= fields.Selection(selection_exterior,string="Radiator")

    Left_Headlight= fields.Selection(selection_exterior,string="Radiator")
    Left_Headlight_img= fields.Selection(selection_exterior,string="Radiator")

    Right_Headlight= fields.Selection(selection_exterior,string="Radiator")
    Right_Headlight_img= fields.Selection(selection_exterior,string="Radiator")

    Left_Headlight= fields.Selection(selection_exterior,string="Radiator")
    Left_Headlight_img= fields.Selection(selection_exterior,string="Radiator")

    Right_Taillight= fields.Selection(selection_exterior,string="Radiator")
    Right_Taillight_img= fields.Selection(selection_exterior,string="Radiator")

    Left_Taillight= fields.Selection(selection_exterior,string="Radiator")
    Left_Taillight_img= fields.Selection(selection_exterior,string="Radiator")

    Right_Taillight= fields.Selection(selection_exterior,string="Radiator")
    Right_Taillight_img= fields.Selection(selection_exterior,string="Radiator")

    Left_Taillight= fields.Selection(selection_exterior,string="Radiator")
    Left_Taillight_img= fields.Selection(selection_exterior,string="Radiator")

    Number_Plate_Lights= fields.Selection(selection_exterior,string="Radiator")
    Number_Plate_Lights_img= fields.Selection(selection_exterior,string="Radiator")

    Number_Plate_Lights= fields.Selection(selection_exterior,string="Radiator")
    Number_Plate_Lights_img= fields.Selection(selection_exterior,string="Radiator")

    Fog_Lights_Working= fields.Selection(selection_exterior,string="Radiator")
    Fog_Lights_Working_img= fields.Selection(selection_exterior,string="Radiator")

    Fog_Lights= fields.Selection(selection_exterior,string="Radiator")
    Fog_Lights_img= fields.Selection(selection_exterior,string="Radiator")

    Reverse_Light= fields.Selection(selection_exterior,string="Radiator")
    Reverse_Light_img= fields.Selection(selection_exterior,string="Radiator")


    Windscreen_Wiper_Rubbers= fields.Selection(selection_exterior,string="Radiator")
    Windscreen_Wiper_Rubbers_img= fields.Selection(selection_exterior,string="Radiator")

# Tyres---------------------------------------------

    Front_Right_Tyre= fields.Selection(selection_tyre,string="Radiator")
    Front_Right_Tyre_img= fields.Selection(selection_tyre,string="Radiator")

    Front_Left_Tyre= fields.Selection(selection_tyre,string="Radiator")
    Front_Left_Tyre_img= fields.Selection(selection_tyre,string="Radiator")

    Rear_Right_Tyre= fields.Selection(selection_tyre,string="Radiator")
    Rear_Right_Tyre_img= fields.Selection(selection_tyre,string="Radiator")

    Rear_Left_Tyre= fields.Selection(selection_tyre,string="Radiator")
    Rear_Left_Tyre_img= fields.Selection(selection_tyre,string="Radiator")

    Spare_Tyre= fields.Selection(selection_tyre,string="Radiator")
    Spare_Tyre_img= fields.Selection(selection_tyre,string="Radiator")

    Brand_Name= fields.Selection(selection_tyre,string="Radiator")
    Brand_Name_img= fields.Selection(selection_tyre,string="Radiator")

    Tyre_Size= fields.Selection(selection_tyre,string="Radiator")
    Tyre_Size_img= fields.Selection(selection_tyre,string="Radiator")

    Rims= fields.Selection(selection_tyre,string="Radiator")
    Rims_img= fields.Selection(selection_tyre,string="Radiator")

    Wheel_Caps= fields.Selection(selection_tyre,string="Radiator")
    Wheel_Caps_img= fields.Selection(selection_tyre,string="Radiator")

# Test drive---------------------------------------------

    Engine_Noise= fields.Selection(selection_drive,string="Radiator")
    Engine_Noise_img= fields.Selection(selection_drive,string="Radiator")

    Engine_Pick= fields.Selection(selection_drive,string="Radiator")
    Engine_Pick_img= fields.Selection(selection_drive,string="Radiator")

    Gear_Shifting= fields.Selection(selection_drive,string="Radiator")
    Gear_Shifting_img= fields.Selection(selection_drive,string="Radiator")

    Drive_Shaft_Noise= fields.Selection(selection_drive,string="Radiator")
    Drive_Shaft_Noise_img= fields.Selection(selection_drive,string="Radiator")

    Brake_Pedal_Operation= fields.Selection(selection_drive,string="Radiator")
    Brake_Pedal_Operation_img= fields.Selection(selection_drive,string="Radiator")

    ABS_Operation= fields.Selection(selection_drive,string="Radiator")
    ABS_Operation_img= fields.Selection(selection_drive,string="Radiator")

    Front_Suspension= fields.Selection(selection_drive,string="Radiator")
    Front_Suspension_img= fields.Selection(selection_drive,string="Radiator")

    Rear_Suspension= fields.Selection(selection_drive,string="Radiator")
    Rear_Suspension_img= fields.Selection(selection_drive,string="Radiator")

    Steering_Operation= fields.Selection(selection_drive,string="Radiator")
    Steering_Operation_img= fields.Selection(selection_drive,string="Radiator")

    Steering_Wheel_Alignment= fields.Selection(selection_drive,string="Radiator")
    Steering_Wheel_Alignment_img= fields.Selection(selection_drive,string="Radiator")

    Heater_Operation= fields.Selection(selection_drive,string="Radiator")
    Heater_Operation_img= fields.Selection(selection_drive,string="Radiator")

    AC_Operation= fields.Selection(selection_drive,string="Radiator")
    AC_Operation_img= fields.Selection(selection_drive,string="Radiator")

    Speedometer= fields.Selection(selection_drive,string="Radiator")
    Speedometer_img= fields.Selection(selection_drive,string="Radiator")









