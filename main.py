# this script takes user inputs to create a feature class and a pdf map
import json,arcpy,os

# grab user's input
mapDocument=arcpy.GetParameterAsText(0)
sybologyLayer=arcpy.GetParameterAsText(1)
outputPDF=arcpy.GetParameterAsText(2)


# function to get JSON data via url
def GetJSONData(url):
    import urllib
    response=urllib.urlopen(url)
    source=response.read()
    return json.loads(source)

# set up workspace
arcpy.env.overwriteOutput = True
arcpy.env.workspace=ws=os.path.join(os.path.dirname(outputPDF),'LinkNYC.gdb')

try:
    # create a geodatabase if it does not exist yet. If it does, remove the old feature class.
    if arcpy.Exists(ws):
        for existingfc in arcpy.ListFeatureClasses('LatestLinkNYCKiosk'):
            arcpy.Delete_management(existingfc)
    else:
        arcpy.management.CreateFileGDB(os.path.dirname(outputPDF),'LinkNYC.gdb')
    
   
    # create a feature class and add fields for data storage
    fc=arcpy.management.CreateFeatureclass(ws,'LatestLinkNYCKiosk','POINT',spatial_reference=4326) # WGS 1984 has wkid=4326
    arcpy.management.AddField(fc, 'generated_on', 'TEXT',field_length=35)
    arcpy.management.AddField(fc, 'site_id','TEXT',field_length=35)
    arcpy.management.AddField(fc, 'status','TEXT',field_length=25)
    arcpy.management.AddField(fc, 'wifi_status','TEXT',field_length=5)
    arcpy.management.AddField(fc, 'phone_status','TEXT',field_length=5)
    arcpy.management.AddField(fc, 'tablet_status','TEXT',field_length=5)
    arcpy.management.AddField(fc, 'address','TEXT',field_length=50)
    arcpy.management.AddField(fc, 'city','TEXT',field_length=10)
    arcpy.management.AddField(fc, 'state','TEXT',field_length=5)
    arcpy.management.AddField(fc, 'zip','TEXT',field_length=10)
    arcpy.management.AddField(fc, 'boro','TEXT',field_length=15)
    arcpy.management.AddField(fc, 'install_date', 'TEXT',field_length=35)
   
    # call function to get JSON data via url
    jsondata=GetJSONData('https://data.cityofnewyork.us/resource/n6c5-95xh.json')
   
    # insert data to feature class's table
    with arcpy.da.InsertCursor(fc,('SHAPE@XY','generated_on','site_id','status','wifi_status','phone_status','tablet_status','address','city','state','zip','boro','install_date')) as cursor:
        for i in jsondata:
            latitude=float(i['latitude'])
            longitude=float(i['longitude'])
            cursor.insertRow(([longitude,latitude],i['generated_on'],i['site_id'],i['status'],i['wifi_status'],i['phone_status'],i['tablet_status'],i['address'],i['city'],i['state'],i['zip'],i['boro'],i['install_date']))
    del cursor
    
    # apply symbology from an existing layer
    mxd=arcpy.mapping.MapDocument(mapDocument) # create a MapDocument object from user input
    df=arcpy.mapping.ListDataFrames(mxd)[0] # get the data frame
    for existinglayer in arcpy.mapping.ListLayers(mxd,'',df):
        if existinglayer.name=='LatestLinkNYCKiosk':
            arcpy.mapping.RemoveLayer(df,existinglayer) # delete existing layer
    arcpy.MakeFeatureLayer_management(fc,'LatestLinkNYCKiosk') # create a layer object in memory 
    layerpath=os.path.join(os.path.dirname(outputPDF),'LatestLinkNYCKiosk.lyr')
    arcpy.SaveToLayerFile_management('LatestLinkNYCKiosk', layerpath, "ABSOLUTE") # save this layer in disk, will be deleted later on
    addLayer=arcpy.mapping.Layer(layerpath) # create a layer object
    arcpy.mapping.AddLayer(df, addLayer, "TOP") # add the layer object to the dataframe
    lyr=arcpy.mapping.ListLayers(mxd,'LatestLinkNYCKiosk')[0]
    sourcelyr=arcpy.mapping.Layer(sybologyLayer) # create a layer object for the symbology layer which comes from user input
    arcpy.mapping.UpdateLayer(df,lyr,sourcelyr) # update symbology

    # get the latest update date
    generatedOn=set()
    for i in jsondata:
        generatedOn.add(int(i['generated_on'][:10].replace('-','')))
    updatedOn=max(generatedOn)
    updatedOnText=str(updatedOn)[:4]+'-'+str(updatedOn)[4:6]+'-'+str(updatedOn)[6:] # create the yyyy-mm-dd format for the update date

    # replace the text element with the latest update date
    for i in arcpy.mapping.ListLayoutElements(mxd,'TEXT_ELEMENT'):
        if i.name=='Updated on':
            i.text=i.text.replace(i.text[11:],updatedOnText)

    arcpy.RefreshActiveView()
    arcpy.mapping.ExportToPDF(mxd,outputPDF)
    arcpy.AddMessage('Created a {} PDF file containing the latest data, and a LatestLinkNYCKiosk feature class in the same directory'.format(os.path.basename(outputPDF)))

except:
    arcpy.AddMessage('Error')
    arcpy.GetMessages()

finally:
    # delete intermediate layer
    if arcpy.Exists(os.path.join(os.path.dirname(outputPDF),'LatestLinkNYCKiosk.lyr')):
        arcpy.Delete_management(os.path.join(os.path.dirname(outputPDF),'LatestLinkNYCKiosk.lyr'))