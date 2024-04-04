# Developer: @bodeby, refactored existing code by @Hans-EH (github)
# Description: Functions utilized in CLI feedback bot, refactored and seperated
# for ease of use in jupyter notebooks.

import pandas as pd
import re
from txtai.pipeline import Translation


# Utilize txtai translation pipeline on text block
# @text : the text block requiring translation
# @lang : the initial language of input
def translate_text(text, lang):
    # Translate the text to a specific language
    target = "en"
    translate = Translation()
    translation = []

    for word in text:
        translated = translate(word, lang, target)
        translation.append(translated)

    return translation


# fixes the awful formatting of the received dataset
# NB: Function assumes 63 columns, first 42 being feedback, and a total of 11 course columns
# @dataframe    : the dataframe to be processed
# @write_file   : decide if the results should be logged
def process_data(dataframe, write_file, should_translate):
    # Create a new DataFrame with selected columns
    new_df = pd.DataFrame(
        columns=[
            "Campus",
            "Semester",
            "Course",
            "Feedback_good",
            "Feedback_bad",
            "Feedback_extra",
        ]
    )
    # Display the new DataFrame

    for index, row in dataframe.iterrows():
        # figure out the campus:
        campus = "Aalborg"
        semester = re.search(r"\d+", row["Semesterbetegnelse"])

        # Check if we can find a semester number in string
        if semester:
            semester = semester.group()
        if "-KBH" in str(row["Semesterbetegnelse"]):
            campus = "Copenhagen"

        # harvesting feedback, assuming 63 columns.
        feedback_good = ""
        feedback_bad = ""
        feedback_extra = ""
        course = ""
        row_arr = row.to_numpy()
        for i in range(0, 42, 3):
            # pd.isna()

            if should_translate:
                feedback_good = translate_text(row_arr[i])
                feedback_bad = translate_text(row_arr[i + 1])
                feedback_extra = translate_text(row_arr[i + 2])
            else:
                feedback_good = row_arr[i]
                feedback_bad = row_arr[i + 1]
                feedback_extra = row_arr[i + 2]

            course = row_arr[int((46 + (i / 3)))]
            if i == 33:
                course = "Project"
            if i == 36:
                course = "Semester"
            if i == 39:
                course = "Studiemiljø"

            if not (
                (pd.isna(feedback_good))
                and (pd.isna(feedback_bad))
                and (pd.isna(feedback_extra))
            ):
                new_row = {
                    "Campus": campus,
                    "Semester": semester,
                    "Course": course,
                    "Feedback_good": feedback_good,
                    "Feedback_bad": feedback_bad,
                    "Feedback_extra": feedback_extra,
                }
                new_df = pd.concat([new_df, pd.DataFrame([new_row])], ignore_index=True)

    if write_file:
        new_df.to_csv("processed_data/proc_dataset.csv", index=False)

    return new_df
