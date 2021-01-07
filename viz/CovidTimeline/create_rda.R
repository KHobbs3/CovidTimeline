######################################################################################
# Input:
# (1) excel file of interventions implemented
# (2) shapefile output from "mergedHR_Top30.ipynb" ("data/shapefiles/cases_top30_dec29.shp")
#
# Outputs .rda files for shiny app
#
# KT Hobbs
########################################################################################

library(here) # file paths
library(rgdal) # reading shapefiles
library(ggplot2) # graphing
library(plotly) # interactivity

# read covid data
master <- rgdal::readOGR(
  dsn= paste0(here(),"/data/input/cases_top30_jan6.shp"), 
  layer="cases_top30_jan6",
  verbose=FALSE
)

# read intervention data
interv <- read.csv(paste0(here(), "/data/input/InterventionScan_Nov_Processed.csv"))

# convert covid date type
master$Date <- as.Date(as.character(master$date_repor), "%Y-%m-%d")

# dataframe
master.df <- as.data.frame(master)

# convert cumulative, daily cases, and date data types 
master.df$cumulative <- as.numeric(as.character(master.df$cumulative))
master.df$cases <- as.numeric(as.character(master.df$cases))

interv$Date <- as.Date(as.character(interv$Date.implemented),"%Y-%m-%d")
interv$suggested_industry <- as.character(interv$suggested_industry )


# clean column names
colnames(interv)[7] = "Intervention"

# save as RData
save(master.df, file = here("/data/output", "covid.rda"))
save(interv, file = here("/data/output/", "interventions.rda"))

