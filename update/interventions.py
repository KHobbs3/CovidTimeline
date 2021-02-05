# Interventions update
choice1 = input("Is there a new CIHI release? (Y/N): ")

if choice1 == "Y":
    import CovidTimeline.wrangle.interventions.CIHIUpdate
    
    choice2 = input("Did you review the updated CIHI file? (Y/N): ")
    if choice2 == "Y":
        import CovidTimeline.wrangle.interventions.interventionUpdate
              
elif choice1 == "N":
    import CovidTimeline.wrangle.interventions.interventionUpdate
