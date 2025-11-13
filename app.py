# get color code of given objekt

import requests
import pandas as pd
import re
import streamlit as st

st.header("Get Objekt Color")

url = "https://apollo.cafe/api/objekts/"

season_dic = {'A': 'Atom01', 'B': 'Binary01', 'C': 'Cream01', 'D': 'Divine01', 'E': 'Ever01',
              'AA': 'Atom02', 'BB': 'Binary02'}
member_order = [
    'SeoYeon', 'HyeRin', 'JiWoo', 'ChaeYeon', 'YooYeon', 'SooMin', 'NaKyoung', 'YuBin', 
    'Kaede', 'DaHyun', 'Kotone', 'YeonJi', 'Nien', 'SoHyun', 'Xinyu', 'Mayu',
    'Lynn', 'JooBin', 'HaYeon', 'ShiOn', 'ChaeWon', 'Sullin', 'SeoAh', 'JiYeon',
    'HeeJin', 'HaSeul', 'KimLip', 'JinSoul', 'Choerry',
    # 'DoHun', 'HeeJu', 'TaeIn', 'JaeYoung', 'JuHo', 'JiWoon', 'HwanHee',
    'tripleS', 'AAA', '+(KR)E', 'TokyoHaus', 'Assemble24', 'S21', 'S22', 'S23', 'S24',
]
multiple_color = ['C324Z', 'D304A', 'D322A', 'D328A', 'D334A']

# define functions

def validate_input(qry):
    """ Check input format. Return (season, collectionNo) or (None, None)"""
    qry = qry.upper().strip()
    if not qry:
        st.error("Please input collection number.") # blank query
        st.stop()

    # check collection format
    pattern = r"^([A-Z]{1,2})(\d{3})([A-Z]?)$"
    match = re.match(pattern, qry)
    if match:
        q_season = match.group(1)
        q_collection = match.group(2)
        q_physical = match.group(3)

        # check season
        if q_season not in season_dic:
            st.error("Wrong input season: Season not found.")
            st.stop()
        else:
            season = season_dic[q_season]

        # check physical
        if q_physical and q_physical == "A":
            physical = True
        elif q_physical and q_physical == "Z":
            physical = False
        else:
            qry += "Z"
            physical = False

        # collection number
        collectionNo = q_collection + 'A' if physical else q_collection + 'Z'

    else:
        st.error("Wrong input format: Please input collection like A101z or D301a.")
        st.stop()

    return qry, season, collectionNo, physical

def get_objekts_data(season, collectionNo, url=url):
    """ 
    呼叫 API 並回傳 objekts 資料 
    API request and get objekts data 
    """
    params = {
        "sort": "noAscending",
        "season": season,
        "collectionNo": collectionNo
    }
    response = requests.get(url, params=params)
    if not response.ok:
        st.error("Request failed. Please try later.")
        st.stop()
    data = response.json().get('objekts', [])
    return data

def custom_sort(x):
    return member_order.index(x['member']), x['createdAt']



##### main 

# Input collection query & check if validate
qry, season, collectionNo, physical = validate_input(
    st.text_input("Enter collection number", value="A301", placeholder="example: A301 or C314a")
)
    
# request & get objekt data
data = get_objekts_data(season, collectionNo)

# if cannot found -> try physical / digital
physical_msg = None
if len(data) == 0:
    if physical:
        collectionNo = collectionNo[:-1] + "Z"
        physical = False
        physical_msg = "Physical not found, changed to digital version."

    else:
        collectionNo = collectionNo[:-1] + "A"
        physical = True
        physical_msg = "Digital not found, changed to physical version."

    data = get_objekts_data(season, collectionNo)

st.write("Objekt name: ", season, collectionNo)

# sort data
data.sort(key=custom_sort)

if len(data):
    if physical_msg:
        st.warning(physical_msg)

    # backgroundColor & textColor
    colors_dict = {}  
    # key = (bgcolor, txtcolor)  -> duple
    # value = {member: [xx, xx]} -> dict { key: lst }

    for objekt in data:

        bgcolor = objekt.get('backgroundColor').upper()
        txtcolor = objekt.get('textColor').upper()
        member = objekt.get('member')
        img = objekt.get('frontImage')
        key = (bgcolor, txtcolor)

        if key not in colors_dict:   # add new color combo (key)
            colors_dict[key] = {
                "members": [member],
                "images": [img] 
                }
            # display color text & imamge
            with st.container():  
                col1, col2 = st.columns(2)
                
                col1.color_picker("", value=bgcolor, key=member+bgcolor)
                col1.markdown(f"Background color: `{bgcolor}`")
                
                col1.color_picker("", value=txtcolor, key=member+txtcolor)
                col1.markdown(f"Text color: `{txtcolor}`")

                col2.image(img, width = 200)

        else:
            colors_dict[key]["members"].append(member) 
    
    # 如果超過一種配色，以表格列出
    if len(colors_dict) > 1:
        table_data = []
        for (bg, tc), info in colors_dict.items():
            # 這裡 info 也是一個 dict，包含 "members", "images", ...
            members_str = ", ".join(info["members"])  # 將多個成員合併成逗號分隔
            table_data.append({
                "member": members_str,
                "backgroundColor": bg,
                "textColor": tc,
            })
        df = pd.DataFrame(table_data)
        st.dataframe(df, hide_index=True)

    if qry in multiple_color:
        st.write("Note: multiple Objekt color")

else:
    st.write("Wrong collection number: Collection not found. Please add `a` for physical objekts.")