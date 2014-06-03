# Author: Bruce Cotton
# Date: 18 September 2013
# Purpose: Determine the ADJACENT relationships between STATE/STATE  and LGA/LGA data.
#              Note the use of INTERSECTS, not BOUNDARY_TOUCHES due to poor geometry

import arcpy

# Set overwrite output
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r"N:\gdmp\DATA\FSDF\Data\Data.gdb"

areaFC = "FSDF_AREA"
spTable = "FSDF_SPATIAL"
spCur = arcpy.InsertCursor (spTable)

# Create layer name to separate STATE and LGA tiers for sequential processing
tierLyr = "tierLyr"
# Create layer name to be used to generate a series of single-feature layers
singleLyr = "singleLyr"

# Set queries to define STATE and LGA layers for processing
tierSqlList = [""""TYPE" = 'STATE' AND "Shape_Area" > 0.2""", """"TYPE" = 'LGA'"""]
for tierSQL in tierSqlList:
  # Create two identical layers (different names) to query against each other ie for each STATE, search neighbouring STATES
  arcpy.MakeFeatureLayer_management (areaFC, tierLyr, tierSQL)
  arcpy.MakeFeatureLayer_management (areaFC, singleLyr, tierSQL)

  theCount = 0
  adjCount = 0

  # Search cursor for single tier subset (ie for each STATE)
  theCur = arcpy.SearchCursor (tierLyr)
  row = theCur.next ()
  while row:
    theCount += 1
    idValue = row.ID
    # Layer name based in ID value
    lyrName = str(idValue) + "_lyr"
    print lyrName
    theSQL = '"ID" = ' + str(idValue)
    # Create 'single feature' layer (lyrName) based on ID
    arcpy.MakeFeatureLayer_management (singleLyr, lyrName, theSQL)
    # Search which STATEs (or LGAs) intersect the selected STATE (or LGA)
    newLyr = arcpy.SelectLayerByLocation_management (tierLyr, "INTERSECT", lyrName)
    subCur = arcpy.SearchCursor (tierLyr)
    subRow = subCur.next()
    while subRow:
      # Compare unit's ID being tested against result IDs, store if not identical
      if idValue <> subRow.ID:
        adjCount += 1
        newAdj = spCur.newRow()
        newAdj.ID = adjCount
        newAdj.UNIT1_ID = idValue       # From polygon being analysed
        newAdj.UNIT2_ID = subRow.ID   # From spatial query result
        newAdj.TYPE = "ADJACENT"
        spCur.insertRow(newAdj)
      print "\t" + subRow.PSMA_ID
      subRow = subCur.next()
    del lyrName
    row = theCur.next ()

del row, theCur, subRow, subCur
