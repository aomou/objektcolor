# get color code of given objekt

import requests
import pandas as pd
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
    'DoHun', 'HeeJu', 'TaeIn', 'JaeYoung', 'JuHo', 'JiWoon', 'HwanHee',
    'tripleS', 'AAA', '+(KR)E', 'TokyoHaus', 'Assemble24', 'S21', 'S22', 'S23', 'S24',
    'idntt',
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
    if len(qry) == 4 and "A" <= qry[0] <= "Z":  
        qry += "Z"
    elif len(qry) == 5 and qry[-1] in ['A', 'Z']:
        pass
    else:
        st.error("Wrong input format: Please input collection like A101z or D301a.")
        st.stop()

    # check season
    if qry[0] not in season_dic:
        st.error("Wrong input season: Season not found.")
        st.stop()
    
    season = season_dic[qry[0]]
    collectionNo = qry[1:]

    return qry, season, collectionNo

def flip_AZ(q): 
    if q.endswith("A"):
        return q[:-1] + "Z"
    elif q.endswith("Z"):
        return q[:-1] + "A"
    return q

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

# Input collection query & check if validate
qry, season, collectionNo = validate_input(
    st.text_input("Enter collection number", value="A301", placeholder="example: A301 or C314a")
)
    
# request & get objekt data
data = get_objekts_data(season, collectionNo)

if len(data) == 0:
    qry = flip_AZ(qry)
    collectionNo = qry[1:]
    data = get_objekts_data(season, collectionNo)

st.write("Objekt name: ", season, collectionNo)

# sort data
data.sort(key=custom_sort)

if len(data):
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