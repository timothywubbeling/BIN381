# app.R  -  launch from the project root with shiny::runApp("app")
# Files in app/R/ (validate.R, score.R, monitor.R) are loaded automatically by Shiny.
library(shiny)
library(bslib)
library(DT)
library(workflows)   # needed so predict() knows how to use the saved workflow

MODEL_PATH <- "../models/final_workflow.rds"   # Thursday: "../models/final_workflow.rds"
THRESHOLD  <- 0.35                                    # Thursday: Person B's chosen threshold

wf        <- readRDS(MODEL_PATH)
reference <- readRDS("../models/reference.rds")

CAVEAT <- paste(
  "This is a screening aid built on 2024 General Household Survey data. It estimates",
  "how similar a household is to households that reported food insecurity; it does not",
  "measure this household's food security and must not be used on its own to approve,",
  "refuse or withdraw any grant, service or support. A trained official reviews every result.")

code_choices <- function(labels) c("Unknown" = "", setNames(seq_along(labels), labels))

ui <- page_navbar(
  title = "Household food-insecurity screening (prototype)",
  nav_panel("Score one household",
    layout_sidebar(
      sidebar = sidebar(width = 340,
        selectInput("ComparativeIncomeCode", "Income compared with a year ago",
                    code_choices(c("Much higher", "Higher", "About the same", "Lower", "Much lower"))),
        selectInput("GeoTypeCode", "Settlement type",
                    code_choices(c("Urban", "Traditional / tribal", "Farms"))),
        numericInput("HouseholdSize", "Household size (people)", 3, min = 1, max = 25),
        numericInput("TotalMonthlyHouseholdIncomeRaw", "Total monthly household income (R)",
                     5000, min = 0),
        checkboxInput("income_unknown", "Income refused / unknown"),
        selectInput("ElectricityAccessCode", "Electricity access", code_choices(c("Yes", "No"))),
        numericInput("SocialGrantRecipients", "Social-grant recipients in household", 0, min = 0, max = 16),
        selectInput("MainToiletCode", "Main toilet facility (GHS code)",
                    code_choices(paste("Code", 1:12))),   # replace with GHS 2024 labels
        actionButton("score_one", "Score household", class = "btn-primary")
      ),
      card(card_header("Result"), uiOutput("one_result")),
      card(card_header("Issues found in the input"), DTOutput("one_issues")),
      card(card_header("How to read this"), p(CAVEAT))
    )
  ),
  nav_panel("Batch upload (CSV)",
    layout_sidebar(
      sidebar = sidebar(width = 340,
        fileInput("csv", "Upload a CSV with the 7 predictor columns", accept = ".csv"),
        downloadButton("download", "Download results"),
        p(class = "small text-muted",
          "Uploads are processed in memory and are not saved. HouseholdID, if present, is",
          "used only to spot duplicates and is never shown or returned. Results keep the",
          "upload's row order so they can be matched back to the source file.")
      ),
      card(card_header("Summary"), uiOutput("batch_summary")),
      card(card_header("Results"), DTOutput("batch_results")),
      card(card_header("Rows with issues"), DTOutput("batch_issues"))
    )
  ),
  nav_panel("About and limits",
    card(
      h4("What this tool is for"),
      p("Screening and prioritising households for follow-up by social-development officials,",
        "provincial planning units and food-relief NGOs. It is not an eligibility test."),
      h4("Model"),
      p("Version: ", reference$model_version, " | trained: ", format(reference$trained_on),
        " | decision threshold: ", THRESHOLD),
      h4("Known limits"),
      tags$ul(
        tags$li("One survey wave (GHS 2024); self-reported food and income items."),
        tags$li("Person-level files (D01-D03) and the labour-market file (D11) are not used."),
        tags$li("Accuracy differs between subgroups; see the fairness section of the report.")
      ),
      p(CAVEAT)
    )
  )
)

server <- function(input, output, session) {

  # ---- single household: the form goes through exactly the same path as a CSV ----
  one <- eventReactive(input$score_one, {
    val <- function(x) if (is.null(x) || identical(x, "") || is.na(x)) NA else as.numeric(x)
    raw <- data.frame(
      ComparativeIncomeCode = val(input$ComparativeIncomeCode),
      GeoTypeCode           = val(input$GeoTypeCode),
      HouseholdSize         = val(input$HouseholdSize),
      TotalMonthlyHouseholdIncomeRaw = if (input$income_unknown) NA else val(input$TotalMonthlyHouseholdIncomeRaw),
      ElectricityAccessCode = val(input$ElectricityAccessCode),
      SocialGrantRecipients = val(input$SocialGrantRecipients),
      MainToiletCode        = val(input$MainToiletCode))
    v <- validate_households(raw)
    list(v = v, s = score_households(wf, v, reference, THRESHOLD))
  })

  output$one_result <- renderUI({
    r <- one()$s
    if (r$status == "not scored")
      return(div(class = "text-danger", strong("Not scored."), " See the issues below."))
    tagList(
      h3(r$predicted),
      p(sprintf("Estimated probability of food insecurity: %.0f%% (referral threshold %.0f%%)",
                100 * r$probability, 100 * THRESHOLD)),
      p(strong("Main contributing factors: "), r$main_factors),
      if (r$status == "scored with warning") p(class = "text-warning", "Scored with warnings - check the issues below.")
    )
  })
  output$one_issues <- renderDT(datatable(one()$v$issues[, -1], rownames = FALSE,
                                          options = list(dom = "t")))

  # ---- batch upload ----
  batch <- reactive({
    req(input$csv)
    raw <- tryCatch(read_upload(input$csv$datapath), error = function(e) NULL)
    validate(need(!is.null(raw), "Could not read this file as a CSV."))
    v <- tryCatch(validate_households(raw), error = function(e) conditionMessage(e))
    validate(need(is.list(v), v))                      # e.g. "Missing required column(s): ..."
    s <- score_households(wf, v, reference, THRESHOLD)
    log_batch(batch_summary(s, reference, THRESHOLD), "../monitoring/batch_log.csv")
    list(v = v, s = s)
  })

  output$batch_summary <- renderUI({
    s <- batch()$s
    p(sprintf("%d rows: %d ok, %d scored with warnings, %d not scored. %d flagged higher risk.",
              nrow(s), sum(s$status == "ok"), sum(s$status == "scored with warning"),
              sum(s$status == "not scored"), sum(s$probability >= THRESHOLD, na.rm = TRUE)))
  })
  output$batch_results <- renderDT(datatable(
    batch()$s[, c("row", "status", "predicted", "probability", "main_factors")], rownames = FALSE))
  output$batch_issues <- renderDT(datatable(batch()$v$issues, rownames = FALSE))

  output$download <- downloadHandler(
    filename = function() paste0("screening_results_", Sys.Date(), ".csv"),
    content  = function(file) {
      out <- batch()$s[, c("row", "status", "predicted", "probability", "main_factors")]
      out$model_version <- reference$model_version
      out$caveat <- "Screening aid only - not an eligibility decision"
      write.csv(out, file, row.names = FALSE)
    })
}

shinyApp(ui, server)
