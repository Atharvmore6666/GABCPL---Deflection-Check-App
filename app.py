import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io

# Define a function to parse the XML file and extract data
def get_deflection_data(xml_file):
    """Parses the XML file and extracts story height and deflection data."""
    root = ET.fromstring(xml_file.getvalue().decode('utf-8'))
    
    # Initialize dictionaries to store max displacements and story heights
    max_displacements = {}
    story_heights = {}
    
    try:
        # Find the story heights from the 'Story_x0020_Definitions' table
        stories_table = root.find(".//Story_x0020_Definitions")
        if stories_table is not None:
            for story in stories_table.findall(".//Story_x0020_Definitions"):
                story_name_elem = story.find("Story")
                if story_name_elem is None or story_name_elem.text is None:
                    continue
                story_name = story_name_elem.text
                
                # Check for both "Height" and "HT" as potential tags
                story_ht_elem = story.find("Height") or story.find("HT")
                if story_ht_elem is not None and story_ht_elem.text is not None:
                    story_ht = float(story_ht_elem.text)
                    story_heights[story_name] = story_ht

        # Find the maximum displacements for each load case
        displacements_table = root.find(".//Story_x0020_Max_x0020_Over_x0020_Avg_x0020_Displacements")
        if displacements_table is not None:
            for disp_data in displacements_table.findall(".//Story_x0020_Max_x0020_Over_x0020_Avg_x0020_Displacements"):
                output_case_elem = disp_data.find("Output_x0020_Case")
                direction_elem = disp_data.find("Direction")
                max_val_elem = disp_data.find("Maximum")

                if output_case_elem is not None and direction_elem is not None and max_val_elem is not None:
                    output_case = output_case_elem.text.replace("-1", "")
                    direction = direction_elem.text
                    max_val = float(max_val_elem.text)
                    
                    # We need to get the max value for each direction (X and Y)
                    if output_case not in max_displacements:
                        max_displacements[output_case] = {'X': 0, 'Y': 0}

                    # Store the max value for the relevant direction
                    if direction == 'X':
                        max_displacements[output_case]['X'] = max(max_displacements[output_case]['X'], max_val)
                    elif direction == 'Y':
                        max_displacements[output_case]['Y'] = max(max_displacements[output_case]['Y'], max_val)
                
    except Exception as e:
        st.error(f"Error parsing XML file: {e}")
        st.stop()
        
    return max_displacements, story_heights

def calculate_deflection_limits(height_mm, load_pattern):
    """Calculates the deflection limit based on the load pattern and height."""
    if load_pattern in ['SPX', 'SPY', 'GX', 'GY']:
        # For SPX/Y and GX/Y, the limit is H/250
        return height_mm / 250.0
    elif load_pattern in ['WX', 'WY']:
        # For WX/Y, the limit is H/500
        return height_mm / 500.0
    else:
        return None

def main():
    """Main function for the Streamlit app."""
    st.set_page_config(page_title="GABCPL", layout="wide")
    st.title("GABCPL - Deflection Check App")
    st.markdown("### A simple tool to check ETABS project deflections.")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload your ETABS XML file", type=['xml'])

    if uploaded_file is not None:
        st.success("File uploaded successfully! Processing data...")
        
        max_displacements, story_heights = get_deflection_data(uploaded_file)
        
        # Determine the maximum story height in millimeters
        max_height_m = 0
        if story_heights:
            max_height_m = max(story_heights.values())
        max_height_mm = max_height_m * 1000
        
        # Prepare data for the DataFrame
        data = []
        # The app now only checks for these 6 specific load patterns
        for lp in ['SPX', 'SPY', 'WX', 'WY', 'GX', 'GY']:
            # The app now correctly handles cases where the load pattern is not available
            if lp in max_displacements:
                actual_def_x = max_displacements[lp].get('X', 0) * 1000
                actual_def_y = max_displacements[lp].get('Y', 0) * 1000
                
                limit_def = calculate_deflection_limits(max_height_mm, lp)
                
                # Check against deflection limit and determine color
                deflection_exceeded_x = actual_def_x > limit_def
                deflection_exceeded_y = actual_def_y > limit_def

                # Append data for X direction
                data.append({
                    "Load Pattern": f"{lp}-X",
                    "Actual Deflection (mm)": f"{actual_def_x:.2f}mm",
                    "Deflection Limit (mm)": f"{limit_def:.2f}mm",
                    "Deflection Limit Formula": f"H/{250 if lp in ['SPX', 'SPY', 'GX', 'GY'] else 500}",
                    "Status": "Exceeded" if deflection_exceeded_x else "OK"
                })
                
                # Append data for Y direction
                data.append({
                    "Load Pattern": f"{lp}-Y",
                    "Actual Deflection (mm)": f"{actual_def_y:.2f}mm",
                    "Deflection Limit (mm)": f"{limit_def:.2f}mm",
                    "Deflection Limit Formula": f"H/{250 if lp in ['SPX', 'SPY', 'GX', 'GY'] else 500}",
                    "Status": "Exceeded" if deflection_exceeded_y else "OK"
                })
            else:
                # If the load pattern is not found, mark it as null
                data.append({
                    "Load Pattern": f"{lp}-X",
                    "Actual Deflection (mm)": "null",
                    "Deflection Limit (mm)": "null",
                    "Deflection Limit Formula": f"H/{250 if lp in ['SPX', 'SPY', 'GX', 'GY'] else 500}",
                    "Status": "null"
                })
                data.append({
                    "Load Pattern": f"{lp}-Y",
                    "Actual Deflection (mm)": "null",
                    "Deflection Limit (mm)": "null",
                    "Deflection Limit Formula": f"H/{250 if lp in ['SPX', 'SPY', 'GX', 'GY'] else 500}",
                    "Status": "null"
                })

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Display results in a table
        st.subheader("Deflection Check Results")
        
        # Apply color to the status column
        def color_status(val):
            if val == "Exceeded":
                return 'background-color: #ff9999'  # Light red for exceeded
            elif val == "OK":
                return 'background-color: #ccffcc'  # Light green for OK
            else:
                return ''
        
        # Apply the style and display the table
        st.dataframe(df.style.applymap(color_status, subset=['Status']))
        
        # Provide an option to export the data to an Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Deflection Report', index=False)
        
        st.download_button(
            label="Download Data as Excel File",
            data=output.getvalue(),
            file_name="Deflection_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.info("Note: The app checks against the maximum story height (H) found in the XML file.")

if __name__ == "__main__":
    main()
