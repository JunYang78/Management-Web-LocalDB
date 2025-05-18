from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os, pandas as pd
import json

BASE_DIR    = os.path.dirname(__file__)
CONFIG_JSON = os.path.join(BASE_DIR, 'file_config.json')
DEFAULT_EXCEL = r'C:\LocalDB\CKENG.xlsx'

def load_excel_path():
    if os.path.exists(CONFIG_JSON):
        try:
            cfg = json.load(open(CONFIG_JSON, 'r', encoding='utf-8'))
            path = cfg.get('data_file')
            if path and os.path.exists(path):
                return path
        except Exception:
            pass
    return DEFAULT_EXCEL

def read_data(sheet_name):
    path = load_excel_path()   
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception as e:
        print(f"Error reading {sheet_name} from {path}: {e}")
        return pd.DataFrame()

app = Flask(__name__)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return "Shutting down"

@app.route('/')
def cu_list():
    df_cu = read_data("CU")
    cu_data = df_cu.to_dict(orient='records')
    return render_template('READ pages/cu_list.html', cu_data=cu_data)

# =============================================================================
#  CREATE 
# =============================================================================

@app.route('/create_cu', methods=['GET', 'POST'])
def create_cu():
    if request.method == 'POST':
        cu_name     = request.form['cu_name']
        cu_location = request.form['cu_location']

        if not os.path.exists(load_excel_path()):
            return "Excel file does not exist.", 404

        try:
            df_cu = pd.read_excel(load_excel_path(), sheet_name="CU")

            if not df_cu.empty:
                nums = (
                    df_cu['CU_ID']
                      .str.extract(r'CU(\d+)', expand=False)
                      .astype(int)
                )
                new_num = nums.max() + 1
            else:
                new_num = 1

            new_cu_id = f"CU{new_num:03}"  

            new_cu = pd.DataFrame({
                'CU_ID':   [new_cu_id],
                'CU_Name': [cu_name],
                'Location':[cu_location]
            })
            df_cu = pd.concat([df_cu, new_cu], ignore_index=True)

            with pd.ExcelWriter(load_excel_path(),
                                engine='openpyxl',
                                mode='a',
                                if_sheet_exists='replace') as writer:
                df_cu.to_excel(writer, sheet_name='CU', index=False)

            return redirect(url_for('cu_list'))

        except PermissionError:
            return "Permission denied. Please ensure the file is closed and writable."
        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('CREATE pages/create_cu.html')

@app.route('/create_fcu/<cu_id>', methods=['GET', 'POST'])
def create_fcu(cu_id):
    if not os.path.exists(load_excel_path()):
        return "Excel file does not exist.", 404

    df_cu = pd.read_excel(load_excel_path(), sheet_name="CU")
    cu_match = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_match.empty:
        return f"CU with ID {cu_id} not found.", 404
    cu = cu_match.iloc[0].to_dict()

    if request.method == 'POST':
        fcu_name = request.form['fcu_name']

        df_fcu = pd.read_excel(load_excel_path(), sheet_name="FCU")

        if not df_fcu.empty:
            nums = (
                df_fcu['FCU_ID']
                  .str.extract(r'FCU(\d+)', expand=False)
                  .astype(int)
            )
            new_num = nums.max() + 1
        else:
            new_num = 1

        new_fcu_id = f"FCU{new_num:03}"  

        new_row = pd.DataFrame([{
            'FCU_ID':   new_fcu_id,
            'FCU_Name': fcu_name,
            'CU_ID':    cu_id
        }])
        df_fcu = pd.concat([df_fcu, new_row], ignore_index=True)

        with pd.ExcelWriter(load_excel_path(),
                            engine='openpyxl',
                            mode='a',
                            if_sheet_exists='replace') as writer:
            df_fcu.to_excel(writer, sheet_name="FCU", index=False)

        return redirect(url_for('cu_details', cu_id=cu_id))

    return render_template('CREATE pages/create_fcu.html', cu=cu)

@app.route('/create_part/<cu_id>', methods=['GET', 'POST'])
def create_part(cu_id):
    if not os.path.exists(load_excel_path()):
        return "Excel file does not exist.", 404

    df_cu = pd.read_excel(load_excel_path(), sheet_name="CU")
    cu_match = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_match.empty:
        return f"CU with ID {cu_id} not found.", 404
    cu = cu_match.iloc[0].to_dict()

    if request.method == 'POST':
        part_name = request.form['part_name']

        df_parts = pd.read_excel(load_excel_path(), sheet_name="CU_Parts")

        if not df_parts.empty:
            nums = (
                df_parts['Part_ID']
                        .str.extract(r'CP(\d+)', expand=False)
                        .astype(int)
            )
            new_num = nums.max() + 1
        else:
            new_num = 1

        new_part_id = f"CP{new_num:03}"  

        new_row = pd.DataFrame([{
            'Part_ID':   new_part_id,
            'CU_ID':     cu_id,
            'Part_Name': part_name
        }])
        df_parts = pd.concat([df_parts, new_row], ignore_index=True)

        with pd.ExcelWriter(load_excel_path(),
                            engine='openpyxl',
                            mode='a',
                            if_sheet_exists='replace') as writer:
            df_parts.to_excel(writer, sheet_name="CU_Parts", index=False)

        return redirect(url_for('cu_details', cu_id=cu_id))

    return render_template('CREATE pages/create_part.html', cu=cu)

@app.route('/create_part_activity/<part_id>', methods=['GET', 'POST'])
def create_part_activity(part_id):
    df_parts = read_data("CU_Parts")
    selected_part = df_parts[df_parts['Part_ID'] == part_id]
    if selected_part.empty:
        return "Part not found", 404
    selected_part = selected_part.iloc[0]

    df_cu = read_data("CU")
    cu = df_cu[df_cu['CU_ID'] == selected_part['CU_ID']].iloc[0]

    if request.method == 'POST':
        name = request.form['activity_name']
        date = request.form['activity_date']
        desc = request.form['description']

        df_act = read_data("CU_Parts_Activity")

        if not df_act.empty:
            nums = (
                df_act['Activity_ID']
                      .str.extract(r'CPA(\d+)', expand=False)
                      .astype(int)
            )
            new_num = nums.max() + 1
        else:
            new_num = 1
        new_id = f"CPA{new_num:03}"  

        new_row = {
            'Activity_ID':   new_id,
            'Part_ID':       part_id,
            'Activity_Name': name,
            'Activity_Date': date,
            'Description':   desc
        }
        df_act = pd.concat([df_act, pd.DataFrame([new_row])], ignore_index=True)

        df_act['Activity_Date'] = pd.to_datetime(df_act['Activity_Date']).dt.date

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl',
                            mode='a', if_sheet_exists='replace') as writer:
            df_act.to_excel(writer, sheet_name="CU_Parts_Activity", index=False)

        return redirect(url_for('cu_part_activities', part_id=part_id))

    return render_template(
        'CREATE pages/create_part_activity.html',
        cu=cu,
        part=selected_part
    )

@app.route('/create_fcu_activity/<fcu_id>', methods=['GET', 'POST'])
def create_fcu_activity(fcu_id):
    df_fcu = read_data("FCU")
    selected_fcu = df_fcu[df_fcu['FCU_ID'] == fcu_id]
    if selected_fcu.empty:
        return "FCU not found", 404
    selected_fcu = selected_fcu.iloc[0]

    df_cu = read_data("CU")
    cu = df_cu[df_cu['CU_ID'] == selected_fcu['CU_ID']].iloc[0]

    if request.method == 'POST':
        name = request.form['activity_name']
        date = request.form['activity_date']
        desc = request.form['description']

        df_act = read_data("FCU_Activity")

        if not df_act.empty:
            nums = (
                df_act['Activity_ID']
                      .str.extract(r'FCA(\d+)', expand=False)
                      .astype(int)
            )
            new_num = nums.max() + 1
        else:
            new_num = 1
        new_id = f"FCA{new_num:03}"  

        new_row = {
            'Activity_ID':   new_id,
            'FCU_ID':        fcu_id,
            'Activity_Name': name,
            'Activity_Date': date,
            'Description':   desc
        }
        df_act = pd.concat([df_act, pd.DataFrame([new_row])], ignore_index=True)

        df_act['Activity_Date'] = pd.to_datetime(df_act['Activity_Date']).dt.date

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl',
                            mode='a', if_sheet_exists='replace') as writer:
            df_act.to_excel(writer, sheet_name="FCU_Activity", index=False)

        return redirect(url_for('fcu_activities', fcu_id=fcu_id))

    return render_template(
        'CREATE pages/create_fcu_activity.html',
        cu=cu,
        fcu=selected_fcu
    )

# =============================================================================
#  EDIT 
# =============================================================================

@app.route('/edit_cu/<cu_id>', methods=['GET','POST'])
def edit_cu(cu_id):
    df_cu = read_data("CU")
    selected_cu = df_cu[df_cu['CU_ID'] == cu_id].iloc[0]

    df_parts = read_data("CU_Parts")
    parts = df_parts[df_parts['CU_ID'] == cu_id].to_dict(orient='records')

    df_fcus = read_data("FCU")
    fcus = df_fcus[df_fcus['CU_ID'] == cu_id].to_dict(orient='records')

    if request.method == 'POST':
        cu_name     = request.form['cu_name']
        cu_location = request.form['cu_location']
        idx = df_cu.index[df_cu['CU_ID'] == cu_id][0]

        df_cu.at[idx, 'CU_Name']  = cu_name
        df_cu.at[idx, 'Location'] = cu_location

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as w:
            df_cu.to_excel(w, sheet_name="CU", index=False)

        return redirect(url_for('cu_details', cu_id=cu_id))

    return render_template('EDIT pages/edit_cu.html', cu=selected_cu, parts=parts, fcus=fcus)

@app.route('/edit_part_activity/<activity_id>', methods=['GET','POST'])
def edit_part_activity(activity_id):
    df_act = read_data("CU_Parts_Activity")
    matched = df_act[df_act['Activity_ID'] == activity_id]
    if matched.empty:
        return f"No activity found with ID {activity_id}", 404
    act_row = matched.iloc[0]

    part_id = act_row['Part_ID']

    df_parts = read_data("CU_Parts")
    part_matched = df_parts[df_parts['Part_ID'] == part_id]
    if part_matched.empty:
        return f"No part found with ID {part_id}", 404
    part = part_matched.iloc[0]
    cu_id = part['CU_ID']

    df_cu = read_data("CU")
    cu_matched = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_matched.empty:
        return f"No CU found with ID {cu_id}", 404
    cu = cu_matched.iloc[0]

    if request.method == 'POST':
        name = request.form['activity_name']
        date = request.form['activity_date']
        desc = request.form['description']

        idx = df_act.index[df_act['Activity_ID'] == activity_id][0]
        df_act.at[idx, 'Activity_Name']  = name
        df_act.at[idx, 'Activity_Date']  = date
        df_act.at[idx, 'Description']    = desc

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_act.to_excel(writer, sheet_name="CU_Parts_Activity", index=False)

        return redirect(url_for('cu_part_activities', part_id=part_id))

    act = act_row.to_dict()
    return render_template(
        'EDIT pages/edit_part_activity.html',
        cu=cu,
        part=part,
        part_id=part_id,
        act=act
    )

@app.route('/edit_fcu_activity/<activity_id>', methods=['GET','POST'])
def edit_fcu_activity(activity_id):
    df_act = read_data("FCU_Activity")
    matched = df_act[df_act['Activity_ID'] == activity_id]
    if matched.empty:
        return f"No activity found with ID {activity_id}", 404
    act_row = matched.iloc[0]

    fcu_id = act_row['FCU_ID']

    df_fcu = read_data("FCU")
    fcu_matched = df_fcu[df_fcu['FCU_ID'] == fcu_id]
    if fcu_matched.empty:
        return f"No FCU found with ID {fcu_id}", 404
    fcu = fcu_matched.iloc[0]
    cu_id = fcu['CU_ID']

    df_cu = read_data("CU")
    cu_matched = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_matched.empty:
        return f"No CU found with ID {cu_id}", 404
    cu = cu_matched.iloc[0]

    if request.method == 'POST':
        name = request.form['activity_name']
        date = request.form['activity_date']
        desc = request.form['description']

        idx = df_act.index[df_act['Activity_ID'] == activity_id][0]
        df_act.at[idx, 'Activity_Name']  = name
        df_act.at[idx, 'Activity_Date']  = date
        df_act.at[idx, 'Description']    = desc

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_act.to_excel(writer, sheet_name="FCU_Activity", index=False)

        return redirect(url_for('fcu_activities', fcu_id=fcu_id))

    act = act_row.to_dict()
    return render_template(
        'EDIT pages/edit_fcu_activity.html',
        cu=cu,
        fcu=fcu,
        fcu_id=fcu_id,
        act=act
    )

@app.route('/edit_part/<part_id>', methods=['GET','POST'])
def edit_part(part_id):
    df_parts = read_data("CU_Parts")
    matched = df_parts[df_parts['Part_ID'] == part_id]
    if matched.empty:
        return f"No part found with ID {part_id}", 404
    part_row = matched.iloc[0]
    part = part_row.to_dict()
    cu_id = part_row['CU_ID']

    df_cu = read_data("CU")
    cu_matched = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_matched.empty:
        return f"No CU found with ID {cu_id}", 404
    cu = cu_matched.iloc[0].to_dict()

    if request.method == 'POST':
        new_name = request.form['part_name']
        idx = df_parts.index[df_parts['Part_ID'] == part_id][0]
        df_parts.at[idx, 'Part_Name'] = new_name

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_parts.to_excel(writer, sheet_name="CU_Parts", index=False)

        return redirect(url_for('cu_details', cu_id=cu_id))

    return render_template(
        'EDIT pages/edit_part.html',
        cu=cu,
        part=part
    )

@app.route('/edit_fcu/<fcu_id>', methods=['GET','POST'])
def edit_fcu(fcu_id):
    df_fcu = read_data("FCU")
    matched = df_fcu[df_fcu['FCU_ID'] == fcu_id]
    if matched.empty:
        return f"No FCU found with ID {fcu_id}", 404
    fcu_row = matched.iloc[0]
    fcu = fcu_row.to_dict()
    cu_id = fcu_row['CU_ID']

    df_cu = read_data("CU")
    cu_matched = df_cu[df_cu['CU_ID'] == cu_id]
    if cu_matched.empty:
        return f"No CU found with ID {cu_id}", 404
    cu = cu_matched.iloc[0].to_dict()

    if request.method == 'POST':
        new_name = request.form['fcu_name']
        idx = df_fcu.index[df_fcu['FCU_ID'] == fcu_id][0]
        df_fcu.at[idx, 'FCU_Name'] = new_name

        with pd.ExcelWriter(load_excel_path(), engine='openpyxl',
                             mode='a', if_sheet_exists='replace') as w:
            df_fcu.to_excel(w, sheet_name="FCU", index=False)

        return redirect(url_for('cu_details', cu_id=cu_id))

    return render_template(
        'EDIT pages/edit_fcu.html',
        fcu=fcu,
        cu=cu
    )

# =============================================================================
#  READ 
# =============================================================================

@app.route('/cu/<cu_id>')
def cu_details(cu_id):
    # 1. Load CU, Parts, FCUs
    df_cu       = read_data("CU")
    selected_cu = df_cu[df_cu['CU_ID'] == cu_id].iloc[0]

    df_parts    = read_data("CU_Parts")
    parts       = df_parts[df_parts['CU_ID'] == cu_id].to_dict(orient='records')
    part_ids    = df_parts[df_parts['CU_ID'] == cu_id]['Part_ID'].tolist()

    df_fcus     = read_data("FCU")
    fcus        = df_fcus[df_fcus['CU_ID'] == cu_id].to_dict(orient='records')
    fcu_ids     = df_fcus[df_fcus['CU_ID'] == cu_id]['FCU_ID'].tolist()

    def lookup_part_name(pid):
        return next((p['Part_Name'] for p in parts if p['Part_ID'] == pid), '')

    def lookup_fcu_name(fid):
        return next((f['FCU_Name'] for f in fcus if f['FCU_ID'] == fid), '')

    raw_part = read_data("CU_Parts_Activity")
    raw_part = raw_part[raw_part['Part_ID'].isin(part_ids)].to_dict(orient='records')

    raw_fcu  = read_data("FCU_Activity")
    raw_fcu  = raw_fcu[raw_fcu['FCU_ID'].isin(fcu_ids)].to_dict(orient='records')

    activities = []

    for act in raw_part + raw_fcu:
        dt = act.get('Activity_Date')
        if isinstance(dt, datetime):
            sort_key = dt
        else:
            sort_key = datetime.strptime(str(dt), '%d-%m-%Y')
        act['_sort_key']     = sort_key
        act['Activity_Date'] = sort_key.strftime('%d-%m-%Y')
        if 'Part_ID' in act:
            act['Source_Type'] = 'Part'
            act['Source_Name'] = lookup_part_name(act['Part_ID'])
        else:
            act['Source_Type'] = 'FCU'
            act['Source_Name'] = lookup_fcu_name(act['FCU_ID'])
        activities.append(act)

    activities.sort(key=lambda x: x['_sort_key'], reverse=True)

    activities = activities[:5]

    for act in activities:
        act.pop('_sort_key', None)

    return render_template(
        'READ pages/cu_details.html',
        cu=selected_cu,
        parts=parts,
        fcus=fcus,
        recent_activities=activities
    )

@app.route('/fcu/<fcu_id>')
def fcu_activities(fcu_id):
    df_fcu = read_data("FCU")
    selected_fcu = df_fcu[df_fcu['FCU_ID'] == fcu_id].iloc[0]

    df_cu = read_data("CU")
    cu = df_cu[df_cu['CU_ID'] == selected_fcu['CU_ID']].iloc[0]

    df_activities = read_data("FCU_Activity")
    activities_raw = df_activities[df_activities['FCU_ID'] == fcu_id].to_dict(orient='records')

    activities = []
    for act in activities_raw:
        raw = act.get('Activity_Date')
        if isinstance(raw, datetime):
            dt = raw
        else:
            try:
                dt = datetime.strptime(str(raw), '%d-%m-%Y')
            except Exception:
                dt = None

        act['date_display'] = dt.strftime('%d-%m-%Y') if dt else ''

        act['date_input']   = dt.strftime('%Y-%m-%d') if dt else ''

        act['_sort_key'] = dt or datetime.min
        activities.append(act)

    activities.sort(key=lambda x: x['_sort_key'], reverse=True)
    for act in activities:
        act.pop('_sort_key', None)

    return render_template(
        'READ pages/fcu_activities.html',
        cu=cu,
        fcu=selected_fcu,
        activities=activities
    )

@app.route('/part/<part_id>')
def cu_part_activities(part_id):
    # — load your part & CU as before —
    df_part = read_data("CU_Parts")
    selected_part = df_part[df_part['Part_ID'] == part_id].iloc[0]

    df_cu = read_data("CU")
    cu = df_cu[df_cu['CU_ID'] == selected_part['CU_ID']].iloc[0]

    # — load activities —
    df_activities     = read_data("CU_Parts_Activity")
    activities_raw    = df_activities[df_activities['Part_ID'] == part_id] \
                        .to_dict(orient='records')

    activities = []
    for act in activities_raw:
        raw = act.get('Activity_Date')
        if isinstance(raw, datetime):
            dt = raw
        else:
            try:
                dt = datetime.strptime(str(raw), '%d-%m-%Y')
            except Exception:
                dt = None

        act['date_display'] = dt.strftime('%d-%m-%Y') if dt else ''

        act['date_input']   = dt.strftime('%Y-%m-%d') if dt else ''

        act['_sort_key'] = dt or datetime.min
        activities.append(act)

    activities.sort(key=lambda x: x['_sort_key'], reverse=True)
    for act in activities:
        act.pop('_sort_key', None)

    return render_template(
        'READ pages/cu_part_activities.html',
        cu=cu,
        part=selected_part,
        activities=activities
    )
# =============================================================================
#  DELETE
# =============================================================================

@app.route('/delete_part_activity/<activity_id>')
def delete_part_activity(activity_id):
    df_act = read_data("CU_Parts_Activity")
    matched = df_act[df_act['Activity_ID'] == activity_id]
    if matched.empty:
        return f"No activity found with ID {activity_id}", 404
    part_id = matched.iloc[0]['Part_ID']

    df_parts = read_data("CU_Parts")
    part_matched = df_parts[df_parts['Part_ID'] == part_id].iloc[0]

    df_new = df_act[df_act['Activity_ID'] != activity_id]

    with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_new.to_excel(writer, sheet_name="CU_Parts_Activity", index=False)

    return redirect(url_for('cu_part_activities', part_id=part_id))

@app.route('/delete_fcu_activity/<activity_id>')
def delete_fcu_activity(activity_id):
    df_act = read_data("FCU_Activity")
    matched = df_act[df_act['Activity_ID'] == activity_id]
    if matched.empty:
        return f"No FCU activity found with ID {activity_id}", 404

    fcu_id = matched.iloc[0]['FCU_ID']

    df_fcu = read_data("FCU")
    fcu_matched = df_fcu[df_fcu['FCU_ID'] == fcu_id]
    if fcu_matched.empty:
        return f"FCU not found with ID {fcu_id}", 404
    cu_id = fcu_matched.iloc[0]['CU_ID']

    df_new = df_act[df_act['Activity_ID'] != activity_id]

    with pd.ExcelWriter(load_excel_path(), engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_new.to_excel(writer, sheet_name="FCU_Activity", index=False)

    return redirect(url_for('fcu_activities', fcu_id=fcu_id))


@app.route('/delete_part/<part_id>')
def delete_part(part_id):
    df_parts     = read_data("CU_Parts")
    df_part_acts = read_data("CU_Parts_Activity")    

    matched = df_parts[df_parts['Part_ID'] == part_id]
    if matched.empty:
        return f"No part found with ID {part_id}", 404

    cu_id = matched.iloc[0]['CU_ID']

    df_parts_new     = df_parts    [df_parts   ['Part_ID'] != part_id]
    df_part_acts_new = df_part_acts[df_part_acts['Part_ID'] != part_id]

    with pd.ExcelWriter(load_excel_path(),
                        engine='openpyxl',
                        mode='a',
                        if_sheet_exists='replace') as writer:
        df_parts_new    .to_excel(writer, sheet_name="CU_Parts",   index=False)
        df_part_acts_new.to_excel(writer, sheet_name="CU_Parts_Activity", index=False)

    return redirect(url_for('cu_details', cu_id=cu_id))

@app.route('/delete_fcu/<fcu_id>')
def delete_fcu(fcu_id):

    df_fcu      = read_data("FCU")
    df_fcu_acts = read_data("FCU_Activity")  

    matched = df_fcu[df_fcu['FCU_ID'] == fcu_id]
    if matched.empty:
        return f"No FCU found with ID {fcu_id}", 404

    cu_id = matched.iloc[0]['CU_ID']

    df_fcu_new = df_fcu[df_fcu['FCU_ID'] != fcu_id]

    df_fcu_acts_new = df_fcu_acts[df_fcu_acts['FCU_ID'] != fcu_id]

    with pd.ExcelWriter(load_excel_path(),
                        engine='openpyxl',
                        mode='a',
                        if_sheet_exists='replace') as writer:
        df_fcu_new      .to_excel(writer, sheet_name="FCU",          index=False)
        df_fcu_acts_new .to_excel(writer, sheet_name="FCU_Activity", index=False)

    return redirect(url_for('cu_details', cu_id=cu_id))

@app.route('/delete_cu/<cu_id>')
def delete_cu(cu_id):
    df_cu        = read_data("CU")
    df_fcus      = read_data("FCU")
    df_parts     = read_data("CU_Parts")
    df_fcu_acts  = read_data("FCU_Activity")   
    df_part_acts = read_data("CU_Parts_Activity")   

    if df_cu[df_cu['CU_ID'] == cu_id].empty:
        return f"No CU found with ID {cu_id}", 404

    df_cu_new = df_cu[df_cu['CU_ID'] != cu_id]

    to_delete_fcu_ids  = df_fcus.loc[df_fcus['CU_ID'] == cu_id, 'FCU_ID'].tolist()
    to_delete_part_ids = df_parts.loc[df_parts['CU_ID'] == cu_id, 'Part_ID'].tolist()

    df_fcus_new  = df_fcus[df_fcus['CU_ID']  != cu_id]
    df_parts_new = df_parts[df_parts['CU_ID'] != cu_id]

    df_fcu_acts_new  = df_fcu_acts[~df_fcu_acts['FCU_ID'].isin(to_delete_fcu_ids)]
    df_part_acts_new = df_part_acts[~df_part_acts['Part_ID'].isin(to_delete_part_ids)]

    with pd.ExcelWriter(load_excel_path(),
                        engine='openpyxl',
                        mode='a',
                        if_sheet_exists='replace') as writer:
        df_cu_new       .to_excel(writer, sheet_name="CU",           index=False)
        df_fcus_new     .to_excel(writer, sheet_name="FCU",          index=False)
        df_parts_new    .to_excel(writer, sheet_name="CU_Parts",         index=False)
        df_fcu_acts_new .to_excel(writer, sheet_name="FCU_Activity",  index=False)
        df_part_acts_new.to_excel(writer, sheet_name="CU_Parts_Activity", index=False)

    return redirect(url_for('cu_list'))

if __name__ == '__main__':
    app.run(debug=True)
