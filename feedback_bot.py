# Original Developer: @Hans-EH (github)
# Description: CLI tool that utilieis Open-Source LLMs to Interactively Analyse and Summarize
# semester feedback by students at aalborg university.

# uses python version 3.9.7
# requirements: pip install pandas langid txtai sacremoses sentencepiece langchain nltk
# before getting started, install ollama
# run command: curl https://ollama.ai/install.sh | sh
# run command: ollama run llama2

import pandas as pd
import re
from langchain.llms import Ollama
import langid
from txtai.pipeline import Translation
import nltk
from nltk.tokenize import word_tokenize
import os

nltk.download("punkt")  # Download the punkt tokenizer data

translate_text_manually = False  # specify if you should translate text manually using "translate_text()". set to false to let Ollama try to translatei t
max_token_context_length = 2000
ollama_model = "llama2"
file_path = "raw_data/complete.csv"  # of the original data


def split_text_into_array(text, max_tokens=20):
    tokens = word_tokenize(text)
    result_array = []

    current_chunk = []
    current_chunk_length = 0

    for token in tokens:
        if current_chunk_length + len(token) <= max_tokens:
            current_chunk.append(token)
            current_chunk_length += len(token)
        else:
            result_array.append(" ".join(current_chunk))
            current_chunk = [token]
            current_chunk_length = len(token)

    if current_chunk:
        result_array.append(" ".join(current_chunk))

    return result_array


# Example usage:


def translate_text(text):
    lang, confidence = langid.classify(text)
    print(lang)
    if lang == "da":
        # Translate the text to a specific language
        translate = Translation()
        translation = []
        for x in text:
            translation.append(translate(x, "da", "en"))
        return translation
    if lang == "sv":
        # Translate the text to a specific language (e.g., Spanish)
        translate = Translation()
        translation = []
        for x in text:
            translation.append(translate(x, "sv", "en"))
        return translation
    if lang == "no":
        # Translate the text to a specific language (e.g., Spanish)
        translate = Translation()
        translation = []
        for x in text:
            translation.append(translate(x, "no", "en"))
        return translation
    return text


# lots queries and its output
def log_query(query, output):
    # Specify the CSV file path
    csv_file_path = "processed_data/log.csv"

    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        # If the file exists, load it into a DataFrame
        log_df = pd.read_csv(csv_file_path)
    else:
        # If the file doesn't exist, generate new data and save it to the CSV file
        log_df = pd.DataFrame(
            columns=[
                "let_llama_translate",
                "max_token_context_length",
                "model",
                "query",
                "output",
            ]
        )
    new_row = {
        "let_llama_translate": translate_text_manually,
        "max_token_context_length": max_token_context_length,
        "model": ollama_model,
        "query": query,
        "output": output,
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
    log_df.to_csv(csv_file_path, index=False)


# fixes the garbage formatting of the data, assuming 63 columns, first 42 being feedback, and a total of 11 course columns
def process_data():
    # Replace 'your_file.csv' with the actual path to your CSV file

    # Load the tab-separated CSV file into a DataFrame
    df = pd.read_csv(file_path, sep="\t", encoding="utf-16")

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

    for index, row in df.iterrows():
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

            if translate_text_manually:
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

    new_df.to_csv("processed_data/processed_dataset.csv", index=False)
    return new_df


def check_strings_in_array(main_string, string_array):
    for substring in string_array:
        if substring.lower() in main_string.lower():
            return [True, substring]
    return [False, ""]


campus = "all"
semester = "all"
course = "all"
df = process_data()
while True:
    
    user_input = input(
        "\nEnter text (type 'exit' to quit). type 'commands' to see available commands: "
    )
    if user_input.lower() == "exit":
        print("Exiting feedbackbot. Goodbye!")
        break
    if "commands".lower() == user_input.lower():
        print(
            "Available commands: \n 'start feedback' to get feedback based upon current query and start chatbot\n 'select campus [campus name]' to select a campus (copenhagen, aalborg) \n 'select semester [semester]' to select a semester. ('semester' is a number between 1 and 10) \n 'select course [course name]' to select a course \n 'get courses' to see available courses \n 'select multiple [campus+course+semester]' to combine query into one line\n 'generate master file' to summarize all course campus combinations into actionable feedback\n 'exit' to exit feedback bot\nNote* to query for all, query for 'all' or leave blank"
        )
    if "select multiple".lower() in user_input.lower():
        if check_strings_in_array(user_input, ["kbh", "cph", "copenhagen", "købehavn"])[
            0
        ]:
            campus = "Copenhagen"
        if check_strings_in_array(user_input, ["aal", "aalborg", "ålborg"])[0]:
            campus = "Aalborg"
        if check_strings_in_array(user_input, df["Course"].unique())[0]:
            course = check_strings_in_array(user_input, df["Course"].unique())[1]
        if check_strings_in_array(
            user_input, ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
        )[0]:
            semester = check_strings_in_array(
                user_input, ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
            )[1]
        print(
            "Campus set to",
            campus,
            ", Semester set to ",
            semester,
            ", Course set to ",
            course,
        )

    if "select campus".lower() in user_input.lower():
        if check_strings_in_array(user_input, ["kbh", "cph", "copenhagen", "købehavn"])[
            0
        ]:
            campus = "Copenhagen"
        if check_strings_in_array(user_input, ["aal", "aalborg", "ålborg"])[0]:
            campus = "Aalborg"
        else:
            campus = "all"
        print("Campus set to ", campus)
    if "select semester".lower() in user_input.lower():
        if check_strings_in_array(
            user_input, ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
        )[0]:
            semester = check_strings_in_array(
                user_input, ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
            )[1]
        else:
            semester = "all"
        print("Semester set to ", semester)

    if "select course".lower() in user_input.lower():
        if check_strings_in_array(user_input, df["Course"].unique())[0]:
            course = check_strings_in_array(user_input, df["Course"].unique())[1]
        else:
            course = "all"
        print("Course set to ", course)

    if "get courses".lower() == user_input.lower():
        print("Available courses: ", df["Course"].unique())

    # iterates all courses (where courses at different campuses are considered unique) and creates a masterfile.
    if "generate master file".lower() == user_input.lower():
        print(
            "starting generation of master file containing actionable feedback for all unique [course,campus]"
        )
        master_df = pd.DataFrame(
            columns=[
                "Campus",
                "Semester",
                "Course",
                "Feedback_good",
                "Feedback_bad",
                "Feedback_extra",
                "Shortened_actionable_feedback",
            ]
        )
        time_total = len(df["Course"].unique())
        time_spent = 0
        for course in df["Course"].unique():
            time_spent += 1
            print("step ", time_spent, "/", time_total)
            df_cpy = df.copy()
            df_cpy_course = df_cpy[df_cpy["Course"] == course]
            for campus in df_cpy_course["Campus"].unique():
                df_cpy_course_campus = df_cpy_course[df_cpy_course["Campus"] == campus]
                for semester in df_cpy_course_campus["Semester"].unique():
                    df_cpy_course_campus_semester = df_cpy_course_campus[
                        df_cpy_course_campus["Semester"] == semester
                    ]
                    if not df_cpy_course_campus.empty:
                        feedback_good = ". ".join(
                            df_cpy_course_campus_semester["Feedback_good"].dropna()
                        )
                        feedback_bad = ". ".join(
                            df_cpy_course_campus_semester["Feedback_bad"].dropna()
                        )
                        feedback_extra = ". ".join(
                            df_cpy_course_campus_semester["Feedback_extra"].dropna()
                        )
                        ollama = Ollama(
                            base_url="http://127.0.0.1:11434", model=ollama_model
                        )
                        # promp engineering
                        feedback = (
                            feedback_good + ". " + feedback_bad + ". " + feedback_extra
                        )
                        feedback_array = split_text_into_array(
                            feedback, max_tokens=max_token_context_length
                        )
                        feedback_array_length = len(feedback_array)
                        shortened_feedback_text = ""
                        for i in range(feedback_array_length):
                            query = (
                                "Summarize, to a maximum of "
                                + str(
                                    int(
                                        (
                                            max_token_context_length
                                            / feedback_array_length
                                        )
                                    )
                                )
                                + " tokens, this text: "
                                + feedback_array[i]
                            )
                            output = ollama(query)
                            shortened_feedback_text += output
                            log_query(query, output)
                        query = (
                            "You are now a actionable feedback bot. Summarize and give actionable feedback based upon this feedback text "
                            + shortened_feedback_text
                        )
                        shortened_actionable_feedback = ollama(query)
                        log_query(query, shortened_actionable_feedback)
                        new_row = {
                            "Campus": campus,
                            "Semester": semester,
                            "Course": course,
                            "Feedback_good": feedback_good,
                            "Feedback_bad": feedback_bad,
                            "Feedback_extra": feedback_extra,
                            "Shortened_actionable_feedback": shortened_actionable_feedback,
                        }
                        master_df = pd.concat(
                            [master_df, pd.DataFrame([new_row])], ignore_index=True
                        )

        master_df.to_csv(
            "processed_data/shortened_actionable_feedback.csv", index=False
        )

    if "start feedback".lower() == user_input.lower():
        print(
            "Starting chatbot based upon the following query: Campus ",
            campus,
            ", Semester ",
            semester,
            ", Course ",
            course,
        )
        df_cpy = df.copy()
        if campus != "all":
            df_cpy = df_cpy[df_cpy["Campus"] == campus]
        if semester != "all":
            df_cpy = df_cpy[df_cpy["Semester"] == semester]
        if course != "all":
            df_cpy = df_cpy[df_cpy["Course"] == course]
        feedback_good = ". ".join(df_cpy["Feedback_good"].dropna())
        feedback_bad = ". ".join(df_cpy["Feedback_bad"].dropna())
        feedback_extra = ". ".join(df_cpy["Feedback_extra"].dropna())
        ollama = Ollama(base_url="http://127.0.0.1:11434", model=ollama_model)
        # promp engineering
        feedback = feedback_good + ". " + feedback_bad + ". " + feedback_extra
        feedback_array = split_text_into_array(
            feedback, max_tokens=max_token_context_length
        )
        feedback_array_length = len(feedback_array)
        shortened_feedback_text = ""
        for i in range(feedback_array_length):
            query = (
                "Summarize, to a maximum of "
                + str(int((max_token_context_length / feedback_array_length)))
                + " tokens, this text: "
                + feedback_array[i]
            )
            output = ollama(query)
            log_query(query, output)
            shortened_feedback_text += output
        query = (
            "You are now a actionable feedback bot. Summarize and give actionable feedback based upon this feedback text "
            + shortened_feedback_text
        )
        output = ollama(query)
        log_query(query, output)
        print(output)
        # print(ollama("You are now an actionable feedback bot. Total feedback must be under 100 words"))
        # print(ollama("The good feedback was: "+feedback_good))
        # print(ollama("The bad feedback was: "+feedback_bad))
        # print(ollama("The extra comments feedback was: "+feedback_extra))
        while True:
            user_input = input(
                "\ndiscuss the feedback with the bot (type 'stop feedback' to stop chatting):\n"
            )
            if user_input.lower() == "stop feedback":
                print("Exiting conversation. Goodbye!")
                break
            query = (
                user_input + " based upon the following text:" + shortened_feedback_text
            )
            output = ollama(query)
            log_query(query, output)
            print(output)
