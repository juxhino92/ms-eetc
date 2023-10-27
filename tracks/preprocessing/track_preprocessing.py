import argparse
import json
import logging
from os import path


def all_keys_in_dictionary(dictionary: dict, key_list: list) -> bool:

    return all(key in dictionary for key in key_list)


def preprocess_curvature(file_content: dict) -> dict:
    """
    Given a dictionary containing a track description with curvatures, keys "radius at start" and 
    "radius at end" are replaced by a single key "radius" whose value is given by:
    1. abs(r), if the value of radius_at_start = value of radius_at_end = r;
    2. average of abs(r1) and abs(r2), if the value of radius_at_start, r1, is different from the value of radius_at_end r2.
    """

    if not "curvatures" in file_content:

        raise ValueError('File does not contain curvature field! Aborting.')
    
    curvatures = file_content['curvatures']

    if not all_keys_in_dictionary(curvatures, ["units", "values"]):

        raise ValueError('\"units\" or \"values\" field is missing! Aborting.')

    if not all_keys_in_dictionary(curvatures["units"], ["position", "radius at start", "radius at end"]):

        raise ValueError('Dictionary must contain \"position\", \"radius at start\", and \"radius at end\" but one (or more) is missing! Aborting.')

    radius_start_index = list(curvatures['units']).index('radius at start')

    radius_end_index = list(curvatures['units']).index('radius at end')

    updated_units = {}

    for k,v in curvatures['units'].items():

        if k == 'radius at start':

            # Appropriately rename the dictionary key
            updated_units['radius'] = v

        elif k != 'radius at end':

            updated_units[k] = v
    
    curvatures['units'] = updated_units

    for track_section in curvatures["values"]:

        # For transition curves, initial and final radius do not coincide.
        if track_section[radius_start_index] == track_section[radius_end_index]:

            track_section[radius_start_index] = abs(track_section[radius_start_index])

        else:

            track_section[radius_start_index] = round((abs(track_section[radius_end_index]) + abs(track_section[radius_start_index]))/2.0, 2)

        del track_section[radius_end_index]  

    file_content["metadata"]["preprocessing"]["curvatures"] = "nonnegative radii; transitions replaced by average of (abs) of involved radii" 
    
    return file_content


def main(input_file: str, output_file: str, curvature: bool):

    try: 

        input_json = open(input_file)

        file_content = json.load(input_json)

        file_content["metadata"]["preprocessing"] = {"original file": path.basename(path.normpath(input_file))}

        updated_content = {}

        if curvature:
                
                updated_content = preprocess_curvature(file_content)

        with open(output_file, 'w') as output_json:

            json.dump(updated_content, output_json, indent=4)

    except Exception as e:

        logging.error("An error occured. Error was: ", e)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Script for processing a track dataset into a form that our optimiser can read.')

    parser.add_argument('input_file', help='Path to input file')

    parser.add_argument('output_file', help='Path to output file')

    parser.add_argument('-c', '--curvature', action='store_true', help='Preprocesses curvature information')

    args = parser.parse_args()

    main(args.input_file, args.output_file, args.curvature)