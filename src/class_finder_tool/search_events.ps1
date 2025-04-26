# Set source and output directories
$PROJECT_ROOT = "YOUR_PROJECT_ROOT"
$OUTPUT_DIR = "OUTPUT_DIR"
$SUFFIX = ""  # Set the desired suffix here


# Run the class finder script with the event-related classes and suffix
python search_classes.py $PROJECT_ROOT $OUTPUT_DIR "class1,class2,class3..." $SUFFIX

Write-Host "Done! Check $OUTPUT_DIR directory for results with suffix '$SUFFIX'."