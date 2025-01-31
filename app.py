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

error_message = ""

# Input collection query 
qry = st.text_input(label="Enter collection number", value="A301", placeholder="example: A301 or C314a").upper().strip()  # strip 移除（前後）空格

if qry:
    if len(qry) == 4 and "A" <= qry[0] <= "Z":  # c302
        qry = qry + "Z"
    elif len(qry) == 5 and qry[-1] == "A" or qry[-1] == "Z":
        qry = qry
    else:
        error_message = "Wrong input format: Please input collection like A101z or D301a."

    if qry[0] in season_dic.keys() and len(error_message) == 0:
        season = season_dic[qry[0]]
        collectionNo = qry[1:]
    elif len(error_message) == 0:
        error_message = "Wrong input season: Season not found."
else:
    # blank input
    error_message = "Please input collection number."

if error_message:
    st.write(error_message)
else:

    params = {
            "sort": "noAscending", 
            "season": season, 
            "collectionNo": collectionNo
            }

    response = requests.get(url, params=params)
    if not response.ok:
        st.write("Request is not successful! Please try later.")
        st.stop()
    data = response.json().get('objekts')

    if len(data) == 0:
        
        if qry[-1] == "A": 
            qry = qry[:-1] + "Z"
        elif qry[-1] == "Z": 
            qry = qry[:-1] + "A"
        collectionNo = qry[1:]

        params = {
            "sort": "noAscending", 
            "season": season, 
            "collectionNo": collectionNo
            }
        response = requests.get(url, params=params)
        if not response.ok:
            st.write("Request is not successful! Please try later.")
            st.stop()
        data = response.json().get('objekts')

    st.write("Objekt name: ", season, collectionNo)

    # sort data
    member_order = [
        'SeoYeon', 'HyeRin', 'JiWoo', 'ChaeYeon', 'YooYeon', 'SooMin', 'NaKyoung', 'YuBin', 
        'Kaede', 'DaHyun', 'Kotone', 'YeonJi', 'Nien', 'SoHyun', 'Xinyu', 'Mayu',
        'Lynn', 'JooBin', 'HaYeon', 'ShiOn', 'ChaeWon', 'Sullin', 'SeoAh', 'JiYeon',
        'HeeJin', 'HaSeul', 'KimLip', 'JinSoul', 'Choerry',
        'tripleS', 'AAA', '+(KR)E', 'TokyoHaus', 'Assemble24', 'S21', 'S22', 'S23', 'S24'
    ]
    def custom_sort(x):
        return member_order.index(x['member']), x['createdAt']
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