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
    place = excel_file_location(file)
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

            if row_values[46] == 'בוצע':
                row_values[46] = True
            else:
                row_values[46] = False

            if row_values[47] == 'בוצע':
                row_values[47] = True
            else:
                row_values[47] = False

            print(row_values[0])

            if true_values and row_values[0] != '' and row_values[0] != ' ' and not pd.isna(row_values[0]):
                if not pd.isna(row_values[1]):
                    new_lab_test = LabTest(location=place, sample_date=row_values[0], analysis_date=row_values[1], ph=row_values[2],
                                           ph_2=row_values[3], ph_average=row_values[4], Alkalinity=row_values[5], ntu=row_values[6],
                                           ntu_2=row_values[7], ave=row_values[8], hardness=row_values[9],
                                           ts_mg=row_values[10], ts_mg_2=row_values[11], ave_ts=row_values[12],
                                           ts_smg=row_values[13], ts_smg_2=row_values[14], ave_tss=row_values[15],
                                           fs_smg=row_values[16], fs_smg_2=row_values[17], ave_fss=row_values[18],
                                           vs_smg=row_values[19], vs_smg_2=row_values[20], ave_vss=row_values[21],
                                           td_smg=row_values[22], td_smg_2=row_values[23], ave_tds=row_values[24],
                                           tp_mg=row_values[25], tp_mg_2=row_values[26], ave_tp=row_values[27],
                                           tn=row_values[28], tn_2=row_values[29], ave_tn=row_values[30],
                                           cod=row_values[31], cod_2=row_values[32], ave_cod=row_values[33],
                                           nh4=row_values[34], nh4_2=row_values[35], ave_nh4=row_values[36],
                                           po4p=row_values[37], po4p_2=row_values[38], ave_po4=row_values[39],
                                           no2=row_values[40], no2_2=row_values[41], ave_no2=row_values[42],
                                           no3=row_values[43], no3_2=row_values[44], ave_no3=row_values[45],
                                           bod=row_values[46], bod2=row_values[47])
                else:
                    new_lab_test = LabTest(location=place, sample_date=row_values[0], ph=row_values[2],
                                           ph_2=row_values[3], ph_average=row_values[4], Alkalinity=row_values[5], ntu=row_values[6],
                                           ntu_2=row_values[7], ave=row_values[8], hardness=row_values[9],
                                           ts_mg=row_values[10], ts_mg_2=row_values[11], ave_ts=row_values[12],
                                           ts_smg=row_values[13], ts_smg_2=row_values[14], ave_tss=row_values[15],
                                           fs_smg=row_values[16], fs_smg_2=row_values[17], ave_fss=row_values[18],
                                           vs_smg=row_values[19], vs_smg_2=row_values[20], ave_vss=row_values[21],
                                           td_smg=row_values[22], td_smg_2=row_values[23], ave_tds=row_values[24],
                                           tp_mg=row_values[25], tp_mg_2=row_values[26], ave_tp=row_values[27],
                                           tn=row_values[28], tn_2=row_values[29], ave_tn=row_values[30],
                                           cod=row_values[31], cod_2=row_values[32], ave_cod=row_values[33],
                                           nh4=row_values[34], nh4_2=row_values[35], ave_nh4=row_values[36],
                                           po4p=row_values[37], po4p_2=row_values[38], ave_po4=row_values[39],
                                           no2=row_values[40], no2_2=row_values[41], ave_no2=row_values[42],
                                           no3=row_values[43], no3_2=row_values[44], ave_no3=row_values[45],
                                           bod=row_values[46], bod2=row_values[47])
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


def excel_file_location(file):
    try:
        # Use pandas to read the Excel file
        df = pd.read_excel(file, header=None)

        # Iterate through rows using iterrows
        for index, row in df.iterrows():
            # Convert the row to a list
            row_values = row.tolist()

            place = 'Nahal Kofer'
            if type(row_values[0]) is str:
                if 'מתניה 2' in row_values[0]:
                    place = 'Metanya Left'
                    break
                elif 'מתניה' in row_values[0]:
                    place = 'Metanya Right'
                    break
                elif 'ספארי' in row_values[0]:
                    place = 'Safari'
                    break
                elif 'פארק לאומי' in row_values[0]:
                    place = 'National Park'
                    break
                elif 'גשר מכביה' in row_values[0]:
                    place = 'Maccabia Bridge'
                    break

        return place

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return 'Nahal Kofer'
