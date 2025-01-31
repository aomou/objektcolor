# get color code of given objekt

import requests
import pandas as pd
import streamlit as st

st.header("Get Objekt Color")

url = "https://apollo.cafe/api/objekts/"

season_dic = {'A': 'Atom01', 'B': 'Binary01', 'C': 'Cream01', 'D': 'Divine01', 'E': 'Ever01'}
member_order = [
    'SeoYeon', 'HyeRin', 'JiWoo', 'ChaeYeon', 'YooYeon', 'SooMin', 'NaKyoung', 'YuBin', 
    'Kaede', 'DaHyun', 'Kotone', 'YeonJi', 'Nien', 'SoHyun', 'Xinyu', 'Mayu',
    'Lynn', 'JooBin', 'HaYeon', 'ShiOn', 'ChaeWon', 'Sullin', 'SeoAh', 'JiYeon',
    'HeeJin', 'HaSeul', 'KimLip', 'JinSoul', 'Choerry',
    'tripleS', 'AAA', '+(KR)E', 'TokyoHaus', 'Assemble24', 'S21', 'S22', 'S23', 'S24'
]
multiple_color = ['C324Z', 'D304A', 'D322A', 'D328A', 'D334A']

# define functions

def validate_input(qry):
    """ Check input format. Return (season, collectionNo) or (None, None)"""
    qry = qry.upper().strip()
    if not qry:
        st.write("Please input collection number.") # blank query
        st.stop()

    # check collection format
    if len(qry) == 4 and "A" <= qry[0] <= "Z":  
        qry += "Z"
    elif len(qry) == 5 and qry[-1] in ['A', 'Z']:
        pass
    else:
        st.write("Wrong input format: Please input collection like A101z or D301a.")
        st.stop()

    # check season
    if qry[0] not in season_dic:
        st.write("Wrong input season: Season not found.")
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

def get_objekts_data(url=url, season, collectionNo):
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
        st.write("Request failed. Please try later.")
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
data = get_objekts_data(url, season, collectionNo)

if len(data) == 0:
    qry = flip_AZ(qry)
    collectionNo = qry[1:]
    data = get_objekts_data(url, season, collectionNo)

st.write("Objekt name: ", season, collectionNo)

# sort data
data.sort(key=custom_sort)

if len(data):
    # backgroundColor & textColor
    colors_set = set()
    colors_lst = [[], []]   # [member], [color] in order

    for i, objekt in enumerate(data):
        bgcolor = objekt.get('backgroundColor').upper()
        txtcolor = objekt.get('textColor').upper()
        member = objekt.get('member')

        if (bgcolor, txtcolor) not in colors_set:   # 如果還沒有此顏色組合
            colors_set.add((bgcolor, txtcolor))  # duple
            colors_lst[0].append(member)
            colors_lst[1].append((bgcolor, txtcolor))

            with st.container():
                col1, col2 = st.columns(2)
                
                col1.color_picker("", value=bgcolor, key=member+bgcolor)
                col1.markdown(f"Background color: `{bgcolor}`")
                
                col1.color_picker("", value=txtcolor, key=member+txtcolor)
                col1.markdown(f"Text color: `{txtcolor}`")

                col2.image(data[i]['frontImage'], width = 200)
        else:
            if member not in colors_lst[0]:  # 如果已經有此顏色組合，但是是不同成員
                i = colors_lst[1].index((bgcolor, txtcolor))
                colors_lst[0][i] = ", ".join([colors_lst[0][i], member])
    
    # 如果超過一種配色，以表格列出
    if len(colors_set) > 1:
        df = pd.DataFrame(
            {
                "member" : [colors_lst[0][i] for i in range(len(colors_lst[0]))], 
                "backgroundColor" : [colors_lst[1][i][0] for i in range(len(colors_lst[0]))], 
                "textColor" : [colors_lst[1][i][1] for i in range(len(colors_lst[0]))]
            }
            )
        st.dataframe(df, hide_index=True)

    if qry in multiple_color:
        st.write("Note: multiple Objekt color")

else:
    st.write("Wrong collection number: Collection not found. Please add `a` for physical objekts.")