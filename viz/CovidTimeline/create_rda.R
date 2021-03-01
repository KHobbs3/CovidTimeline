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
  dsn= paste0(here(),sprintf("/data/input/cases_%s.shp",Sys.Date())), 
  layer=sprintf("cases_%s", Sys.Date()),
  verbose=FALSE
)

# read intervention data
interv <- read.csv(paste0(here(), sprintf("/data/input/InterventionScan_Processed_%s.csv",Sys.Date())))

# convert covid date type
master$Date <- as.Date(as.character(master$date_repor), "%Y-%m-%d")

# dataframe
master.df <- as.data.frame(master)

# convert cumulative, daily cases, and date data types 
master.df$cumulative <- as.numeric(as.character(master.df$cumulative))
master.df$cases <- as.numeric(as.character(master.df$cases))

interv$Date <- as.Date(as.character(interv$Implemented),"%Y-%m-%d")


# clean column names
colnames(interv)[5] = "Health Region"
colnames(interv)[7] = "Intervention"
colnames(interv)[12] = "Source type"
colnames(master.df)[6] = "Health Region"

# subset ----
# curate intervention columns

interv_sub <- interv[,c("Jurisdiction", "Health Region", "Implemented", 
                        "Intervention", "Type", "Summary", "Industry",
                        "Date", "Source type")]

# order by date
interv_sub <- interv_sub[order(interv_sub$Implemented),]

master.df <- master.df[, c("POPCTRRAui", "POPCTRRAna", "Health.Region", "Province", "cases", "cumulative",
                           "SourceURL", "SHAPE_Leng", "SHAPE_Area", "Date")]

# save as RData
save(master.df, file = here("/data/output", "covid.rda"))
save(interv_sub, file = here("/data/output/", "interventions.rda"))

