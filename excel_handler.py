from datetime import datetime
import pandas as pd
from website import db
from website.models import LabTest


def validate_excel_file(file):
    try:
        # Use pandas to read the Excel file
        df = pd.read_excel(file, header=None)

        # Specify the values to check in each row
        target_values = ['PH', 'Alkalinity mg/l', ' hardness mg/l']

        # Iterate through rows using iterrows
        for index, row in df.iterrows():
            # Convert the row to a list
            row_values = row.tolist()

            if all(value in row_values for value in target_values):
                return True

        return False

    except Exception as e:
        print(f"Error reading Excel file: {e}")


def extract_excel_file(file):
    true_values = False
    try:
        # Use pandas to read the Excel file
        df = pd.read_excel(file, header=None)

        # Specify the values to check in each row
        target_values = ['PH', 'Alkalinity mg/l', ' hardness mg/l']

        # Iterate through rows using iterrows
        for index, row in df.iterrows():
            # Convert the row to a list
            row_values = row.tolist()

            # Convert the first item to a date object
            if row_values and isinstance(row_values[1], str):
                try:
                    row_values[1] = datetime.strptime(row_values[1], '%d.%m.%Y').date()
                except ValueError:
                    pass

            if row_values and isinstance(row_values[2], str):
                try:
                    row_values[2] = datetime.strptime(row_values[2], '%d.%m.%Y').date()
                    print(type(row_values[1]))
                except ValueError:
                    pass

            # Remove the item at index 0
            row_values = row_values[1:]

            if row_values[44] == 'בוצע':
                row_values[44] = True
            else:
                row_values[44] = False

            if row_values[45] == 'בוצע':
                row_values[45] = True
            else:
                row_values[45] = False

            if true_values and row_values[0] != '' and row_values[0] != ' ' and not pd.isna(row_values[0]):
                if not pd.isna(row_values[1]):
                    new_lab_test = LabTest(sample_date=row_values[0], analysis_date=row_values[1], ph=row_values[2],
                                           ph_2=row_values[3], ph_average=row_values[4], ntu=row_values[5],
                                           ntu_2=row_values[6], ave=row_values[7], hardness=row_values[8],
                                           ts_mg=row_values[9], ts_mg_2=row_values[10], ave_ts=row_values[11],
                                           ts_smg=row_values[11], ts_smg_2=row_values[12], ave_tss=row_values[13],
                                           fs_smg=row_values[14], fs_smg_2=row_values[15], ave_fss=row_values[16],
                                           vs_smg=row_values[17], vs_smg_2=row_values[18], ave_vss=row_values[19],
                                           td_smg=row_values[20], td_smg_2=row_values[21], ave_tds=row_values[22],
                                           tp_mg=row_values[23], tp_mg_2=row_values[24], ave_tp=row_values[25],
                                           tn=row_values[26], tn_2=row_values[27], ave_tn=row_values[28],
                                           cod=row_values[29], cod_2=row_values[30], ave_cod=row_values[31],
                                           nh4=row_values[32], nh4_2=row_values[33], ave_nh4=row_values[34],
                                           po4p=row_values[35], po4p_2=row_values[36], ave_po4=row_values[37],
                                           no2=row_values[38], no2_2=row_values[39], ave_no2=row_values[40],
                                           no3=row_values[41], no3_2=row_values[42], ave_no3=row_values[43],
                                           bod=row_values[44], bod2=row_values[45])
                else:
                    new_lab_test = LabTest(sample_date=row_values[0], ph=row_values[2],
                                           ph_2=row_values[3], ph_average=row_values[4], ntu=row_values[5],
                                           ntu_2=row_values[6], ave=row_values[7], hardness=row_values[8],
                                           ts_mg=row_values[9], ts_mg_2=row_values[10], ave_ts=row_values[11],
                                           ts_smg=row_values[11], ts_smg_2=row_values[12], ave_tss=row_values[13],
                                           fs_smg=row_values[14], fs_smg_2=row_values[15], ave_fss=row_values[16],
                                           vs_smg=row_values[17], vs_smg_2=row_values[18], ave_vss=row_values[19],
                                           td_smg=row_values[20], td_smg_2=row_values[21], ave_tds=row_values[22],
                                           tp_mg=row_values[23], tp_mg_2=row_values[24], ave_tp=row_values[25],
                                           tn=row_values[26], tn_2=row_values[27], ave_tn=row_values[28],
                                           cod=row_values[29], cod_2=row_values[30], ave_cod=row_values[31],
                                           nh4=row_values[32], nh4_2=row_values[33], ave_nh4=row_values[34],
                                           po4p=row_values[35], po4p_2=row_values[36], ave_po4=row_values[37],
                                           no2=row_values[38], no2_2=row_values[39], ave_no2=row_values[40],
                                           no3=row_values[41], no3_2=row_values[42], ave_no3=row_values[43],
                                           bod=row_values[44], bod2=row_values[45])
                try:
                    db.session.add(new_lab_test)
                    db.session.commit()
                except Exception as e:
                    print(f"Error reading Excel file: {e}")
                    return False

            if all(value in row_values for value in target_values):
                true_values = True

        return True

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False
