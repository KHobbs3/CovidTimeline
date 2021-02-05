#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(shinydashboard)
library(ggplot2) # graphing
library(plotly) # interactivity


# load data
load(file = "data/output/covid.rda")  
load(file = "data/output/interventions.rda")


# Set Variables -----
# curate intervention columns
interv_sub <- interv[,c("Jurisdiction", "health_region", "Date.announced", "Date.implemented", 
          "Intervention", "Intervention.type", "Intervention.summary", "suggested_industry",
          "Date", "Source.type")]

# order by date
interv_sub <- interv_sub[order(interv_sub$Date.implemented),]

# define industry types
types <- c("Activities", "Fitness", "General merchandise stores", "Nightlife", "Personal care", "Restaurants & eating places")

#-----------------

# Define UI ------
ui <- fluidPage(
    
    # Application title
    titlePanel("COVID-19 Cases and Interventions by Health Region"),
    h4("Canada's Top 30 Population Centres"),
    
    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            selectInput("region", "Health Region or Authority", 
                        choices=sort(unique(master.df$health_reg))),
            helpText("Select a health region or authority."),
            
            selectizeInput(inputId = "industry", label = h5("Industry"), 
                         choices = types,
                         selected = types,
                         multiple = T),
            helpText("Filter by operations impacted by policy interventions."),
            hr(),
            radioButtons(inputId = "check", label = h5("Cases"), 
                         choices = list("Cumulative" = "Cumulative", "Weekly" = "Weekly"),
                         selected = "Cumulative",
                         inline = T),
            
           hr(),
          checkboxGroupInput("source", "Source", 
                      choices=c("Government" = "Government", "CIHI" = "CIHI", "News" = "News"),
                      selected = c("Government", "CIHI", "News"),
                      inline = T),
          helpText("Select policy intervention data source."),
          hr()
        ),


        
        # Show a plot of the generated distribution
        mainPanel(
            plotlyOutput("tsPlot"),
            helpText("Graph shows data from July 20, 2020 - February 2, 2021."),
            hr(),            
            tableOutput('table'),
            hr(),
            tags$cite('Sources:'),
            tags$br(),
            tags$br(),
            tags$cite('Berry I, Soucy J-PR, Tuite A, Fisman D. Open access epidemiologic data and an interactive dashboard to monitor the COVID-19 outbreak in Canada. CMAJ. 2020 Apr 14;192(15):E420. doi: https://doi.org/10.1503/cmaj.75262.'),
            tags$br(),
            tags$br(),
            tags$cite("Canadian Institute for Health Information. COVID-19 Intervention Scan — Data Tables. Ottawa, ON: 
CIHI; October 21, 2020."),
            tags$br(),
            tags$br(),
            tags$cite('For a complete list of sources pertaining to Covid-19 interventions, download the excel file:'),
            tags$a(href = "https://github.com/KHobbs3/COVID-Cases-Interventions/blob/main/viz/CovidTimeline/data/input/InterventionScan_Nov_Processed.csv", "Excel.")
        )
    )
)

# Define server logic -----
server <- function(input, output, session) {
    
    output$tsPlot <- renderPlotly({
        
        # user input --- subset by health region. For Ottawa, only plot Ottawa - Gatineau (same data as Kanata)
        if (input$region == "Ottawa"){
            reg <- subset(master.df, master.df$POPCTRRAna == "Ottawa - Gatineau")
        } else {
            reg <- subset(master.df, master.df$health_reg == input$region)
        }
        
        # user input --- checkbox
        if (input$check == "Cumulative"){
            Cases <- reg$cumulative
        } else if (input$check == "Weekly"){
            Cases <- reg$cases
        }
        
        # y limits
        m <- max(Cases)
        
        
        # user input --- filter intervention data
        interv_sub <- subset(interv_sub, interv_sub$health_region == input$region & interv_sub$Source.type %in% input$source)
          # by industry tag
        # interv_sub <- interv_sub[grepl(paste(input$industry,collapse="|")),]
        
        # create plot ---
        g <- ggplot(reg, aes(x=Date, y=Cases))  +
            
            # plot this
            geom_area(fill="#69b3a2", alpha=0.4) +
            geom_line(color="#69b3a2", size=0.5) +
      
            # aesthetics
            ggtitle(sprintf("%s reported cases of COVID-19 in %s", input$check, input$region)) +
            ylim(0, m) + 
            labs(y = "", x = "")
        
        # if there is intervention data for the user-selected region, plot it
        if (nrow(interv_sub) != 0){
            g = g + geom_vline(data = interv_sub, aes(xintercept= as.numeric(Date), linetype=Intervention),
                             na.rm = TRUE)} 
        
        # show
        ggplotly(g)
        
        
        
    })
    
    # create intervention table
    output$table <- renderTable({
        # user input --- filter intervention data
      out <- subset(interv_sub, interv_sub$health_region == input$region & interv_sub$Source.type %in% input$source)
      
      # out[grepl(paste(input$industry,collapse="|"),
      #              interv_sub$suggested_industry),c("Jurisdiction", "health_region", "Date.implemented", "Intervention",
      #                                                                     "Intervention.type", "Intervention.summary", "suggested_industry", "Source.type")]
      out[,c("Jurisdiction", "health_region", "Date.implemented", "Intervention",
                                                 "Intervention.type", "Intervention.summary", "suggested_industry", "Source.type")]
      
    })
}


# Run the application -----
shinyApp(ui = ui, server = server)