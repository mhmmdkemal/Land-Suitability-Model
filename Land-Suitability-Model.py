#LandSuitabilityModel.py
# Name:         Mohammed Kemal
# Purpose:      This script will reclassify DEM and landuse raster data as defined by user, and then it will
#               calculate "best site" values in order to help user find suitable lands for house construction.
# Date:         2/22/2015

#this imports all the modules listed below 
import arcpy, math, sys     ##unused modules imported

#This creates a license exception which passes
class LicenseError(Exception):
    pass

#This Creates a weight exception which passes
class WeightError(Exception):
    pass

#is the start of our code where th try function starts 
try:
    #Check the ArcGIS Spatial Analyst extension license back
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    else:
        # Raise a custom exception
        raise LicenseError

    #This overwrite the files that are created 
    arcpy.env.overwriteOutput = True    

    #open the DEM input raster with get slope and aspect data 
    inrasterDEM = arcpy.GetParameterAsText(0)
        
    #these are the parameters (userinputs) that are requested in arcMap
    inrasterLU = arcpy.GetParameterAsText(1)
    arcpy.env.workspace = arcpy.GetParameterAsText(2)
    W1 = float(arcpy.GetParameterAsText(3))
    W2 = float(arcpy.GetParameterAsText(4))
    RasterName = arcpy.GetParameterAsText(5)
    
    #calculate Slope from DEM raster and reclassify the results
    outSlope = arcpy.sa.Slope(inrasterDEM, "DEGREE")
    reclassSlope = arcpy.sa.Reclassify(outSlope, "Value", arcpy.sa.RemapRange([[0,3,3],[3,6,2],[6,90,1]]))
        
    #calculate Aspect from DEM raster and reclassify the results
    OutAspect = arcpy.sa.Aspect(inrasterDEM)
    reclassAspect = arcpy.sa.Reclassify(OutAspect, "Value", arcpy.sa.RemapRange([[-1,0,3],[0,45,1],[45,113,2],[113,203,3],[203,315,2],[315,360,1]]))

    #reclassify the landuse layer and select the output landuse raster
    reclassLU = arcpy.sa.Reclassify(inrasterLU, "Value", arcpy.sa.RemapRange([[0,17,0],[18,18,1],[19,72,0],[73,73,1],[74,242,0]]))

    #this lets us run if statements to catch user error from the W1
    ####It is more efficient to check weight conditions before you calculate slope, aspect, etc.
    
    ###condition is wrong. This if condition never be satistifed. You check W1 >1 AND w1 <0 --never satisfied
    if 0 > W1 >1:          ## if W1 <0 or W1>1            
        print W1
        raise WeightError   ###Better to pass different error messages for different invalid error conditions
        #
    if 0 > W2 >1:          ##the same as above
        raise WeightError
    if W1+W2 >1:    ### condition is not proper. It shuld be equal to 1
        raise WeightError

    #this calculaets and creates the best site 
    BestSite = (((W1)*(reclassAspect) + (W2)*(reclassAspect)) * (reclassLU))
    BestSite.save(RasterName)
  
    ###delete all the tempoary files by calling 
    ###del outSlope, outAspect, ..... or  arcpy.Delete_management(outSlope, "Raster")       
#This is where the error is printed, if there was an error for the weights 
except WeightError, e:
    print e

#This is where the error is printed, if there was an error for the license
except LicenseError:
    print "3D Analyst license is unavailable"  

#This is where the error is printed, if there was an error for the entire code from the try function
except Exception, e:
    print e
    print arcpy.GetMessages("Please check if weights total to one and neither one is less than zero or greater than 1")

#everything in here lets us either check extentions or any other command we input 
finally:
    arcpy.CheckInExtension("Spatial")
