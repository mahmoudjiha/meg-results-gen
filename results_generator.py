import os
import argparse
import copy
from epilepsy_slides import *

DATE_FORMAT = re.compile(r"\d{1,2}/\d{1,2}/\d{4}$")

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ica', action='store_true',
                    help='include ICA in event legend')
args = parser.parse_args()

def prompt(prompt_str):
    return input('>>> ' + prompt_str)

def evaluate_date_format(date_str):
    return(isinstance(DATE_FORMAT.match(date_str), re.Match))

def get_exam_date(exam_type):
    correct_format = False

    while correct_format is False:
        date = prompt(PROMPTS[exam_type]).rstrip()

        if evaluate_date_format(date):
            correct_format = True

    return date

def get_demographics():
    print(PROMPTS['NAME_REQUEST'])
    first_name = prompt(PROMPTS['FIRST_NAME']).rstrip()
    last_name = prompt(PROMPTS['LAST_NAME']).rstrip()

    mri_date = get_exam_date('MRI')
    meg_date = get_exam_date('MEG')

    meg_month, meg_day, meg_year = meg_date.rsplit("/")

    if len(meg_month) == 1:
        meg_month = '0' + meg_month

    if len(meg_day) == 1:
        meg_day = '0' + meg_day

    prs_date = meg_year + meg_month + meg_day

    global final_prs_name
    final_prs_name = last_name + first_name[0] + '_' + prs_date + '_' + 'MSI.pptx'

    demos = f"{first_name} {last_name}, MRI {mri_date}, MEG {meg_date}"

    return demos

def separate_by_instrument(filename_list, repetitions):
    separated = [[],[],[]]

    for n in range(len(separated)):
        for i in range(repetitions):
            separated[n].append(filename_list.pop())

    return separated

def sort_filenames(data_type, separated):
    """
    Sorts filenames according to the numerical characters at the end of the string
    """
    #check length of sublist at 0 index, return if < 10
    #check length of element of sublist at 0 index
    #isolate elements with equivalent length into a new list, list 1
    #sort list
    #add to new sorted array
    #when list is empty, check if initial list is empty
    #if not...repeat with next
    #

    sorted_list = []

    if data_type not in MRI_ONLY:
        for i in range(len(separated)):
            character_count = len(separated[i][0])
            partial_list = []
            duplicate_list = copy.deepcopy(separated[i])

            for n in range(len(separated[i])):

                if len(separated[i][n]) == character_count:
                    isolated = separated[i][n]
                    partial_list.append(isolated)
                    duplicate_list.remove(isolated)

            partial_list.sort()
            new_list = partial_list + duplicate_list
            sorted_list.append(new_list)


    elif data_type in MRI_ONLY:
        if len(separated) < 10:
            return separated

        character_count = len(separated[0])
        partial_list = []
        duplicate_list = copy.deepcopy(separated)

        for n in range(len(separated)):
            if len(separated[n]) == character_count:
                isolated = separated[n]
                partial_list.append(isolated)
                duplicate_list.remove(isolated)

        partial_list.sort()
        sorted_list = partial_list + duplicate_list

    return sorted_list

def get_data_files(data_type: str) -> list:
    """
    Obtains a list of all filenames in the directory
    Isolates meg, eeg, mri images into lists
    Checks if all three lists have an equal number of elements -> throws error if not
    Returns a list with lists of filenames of the data type isolated by instrument type for a data type.
    """

    subject_id_pattern = r"C\d{4}[A-Z]\."


    if data_type == 'sam':
        instrument_pattern = r"[a-zA-Z]{3}\.R\d{1,2}V\d{1,2}\."
    else:
        instrument_pattern = r"[a-zA-Z]{3}\."


    datatype_pattern = data_type + r"\d{1,2}\.png$"
    filename_pattern = subject_id_pattern + instrument_pattern + datatype_pattern
    pattern = re.compile(filename_pattern)
    directory_filelist = os.listdir()
    raw_files = []

    for file_name in directory_filelist:
        if pattern.match(file_name):
            raw_files.append(file_name)

    raw_files.sort()

    raw_file_count = len(raw_files)


    if raw_file_count < 3 and data_type not in MRI_ONLY or raw_file_count < 1:
        return()
    elif data_type in MRI_ONLY:
        data_files = raw_files
        sorted_files = sort_filenames(data_type, data_files)
        # event_count = raw_file_count
    else:
        event_count = raw_file_count // 3
        separated_files = separate_by_instrument(raw_files, event_count)

        if (len(separated_files[0]) != len(separated_files[1]) or
            len(separated_files[0]) != len(separated_files[2])):
            print('Error....')
            exit()

        sorted_files = sort_filenames(data_type, separated_files)

    return sorted_files

def evaluate_folder():
    """
    """

    filename_dictionary = {}

    for data_type in TYPE_LIST:
        file_names = get_data_files(data_type)

        if len(file_names) > 0:
            filename_dictionary[data_type] = file_names

    return filename_dictionary

def generate_epilepsy_results(presentation):
    '''
    1. Prompt user for patient name, mri date, meg date
    2. Store filetypes in dictionary
        a. obtain a list of all filenames in the directory
        b. Isolate filenames for each datatype and store in a dictionary
    3. Create a slide for events of each data type
        a. insert demographics, images, text, shapes
        b. check filename dictionary for keys matching data types
            - if present, add to legend on each slide
                * exclude SAM from legend for sef, cor, motor slides
    4. Save presentation
    '''

    patient_info = get_demographics()

    file_names = evaluate_folder()

    included_types = file_names.keys()
    legend_types = copy.deepcopy(list(included_types))

    if args.ica:
        legend_types.append('ica')

    if 'cor' in legend_types:
        legend_types.remove('cor')

    for key in included_types:
        if key not in MRI_ONLY:
            for i in range(len(file_names[key][0])):
                current_images = []
                current_images.append(file_names[key][0][i])
                current_images.append(file_names[key][1][i])
                current_images.append(file_names[key][2][i])

                create_slide(presentation, key, current_images, patient_info, legend_types)
        elif key in MRI_ONLY:
            for i in range(len(file_names[key])):
                create_slide(presentation, key, file_names[key][i], patient_info, legend_types)

    presentation.save(final_prs_name)

generate_epilepsy_results(Presentation('epi-template.pptx'))
