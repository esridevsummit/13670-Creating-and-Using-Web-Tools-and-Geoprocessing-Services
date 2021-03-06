#************************************************************************************************************#
#                                                                                                            #
#               This script demonstrates how to publish a web tool using arcpy functions                     #
#                                                                                                            #
#                               2022 Developer Summit    Esri GP Service team                                #
#                                                                                                            #
#************************************************************************************************************#


import arcpy
import config
import os
import sys

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# Set workspace and scratch folder
ws = arcpy.env.workspace = config.workspace
sc = config.scratchworkspace
servername = config.fedservername


# Sign in Portal
try:
    arcpy.SignInToPortal('https://{}/portal/'.format(config.portalname), config.username, config.password)
    print('Signed in to portal')
except:
    print("Signin error:", sys.exc_info()[0])


# Set input and output data then run the model
intbx = 'Dev2022.tbx'
inputfc = os.path.join('Dev2022.gdb', 'calls')
try:    
    inputRaster= arcpy.management.MakeRasterLayer('stowe_elev.tif','stowe_lyr')
    distance_method ='Manhattan'
    arcpy.ImportToolbox(intbx)
    result_item = arcpy.Dev2022.hotspotscript(inputfc, inputRaster, distance_method)
    print("Tool runs successfully.")

except:
    print("Making layer or running tool error:", sys.exc_info()[0])    
    
 
# Publish web tool
try:    
    # Create a service definition draft
    draft_file = os.path.join(sc,'webtools.sddraft')
    draft_file_return = arcpy.CreateGPSDDraft(result = result_item,
                                          out_sddraft = draft_file,
                                          service_name = 'hotspotwebtool',
                                          server_type = "MY_HOSTED_SERVICES", 
                                          constantValues = ['hotspotscript.distancem'])
    print("Service Definition Draft is ready.")
    
    # Analyze the return from creating the service definition draft
    if (draft_file_return['errors']):
        print(draft_file_return['errors'])
    else:
        print(draft_file_return['warnings'])
    
        # Stage the service
        definition_file = os.path.join(sc, 'webtools.sd')
        arcpy.StageService_server(draft_file, definition_file)
        print("Service staged.")
    
        # Upload service definition
        arcpy.UploadServiceDefinition_server(definition_file,'https://{}/server'.format(servername))
        print("Service published.")
except:
    print("Publishing error:", sys.exc_info()[0])    