import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO

# スプレッドシートの認証
scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
]
credentials = service_account.Credentials.from_service_account_file( 'bbtapp230403-715595753eb1.json', scopes=scopes
)
gc = gspread.authorize(credentials)
# スプレッドシートからデータ取得

SP_SHEET_KEY2 = '12MyuKNAo7vszl7qOti3mNwHLiymsNH4AghzT5Ge8D2c'# スプレッドシートのキー
sh2 = gc.open_by_key(SP_SHEET_KEY2)

ws_list = sh2.worksheets()
ws_name_list = []
for i  in range(len(sh2.worksheets())):
    ws_name_list.append(ws_list[i].title)
game_list = ws_name_list[1:]
selected_games = st.multiselect("Games",game_list)

if selected_games is not None:
    all_data = []
    for game in selected_games:
        ws = sh2.worksheet(game)
        data = ws.get_all_values() # シート内の全データを取得
        all_data = all_data + data[1:]
    col = ["回","攻撃","投手","捕手","打者","打","アウト","塁","カウント","構え","球速","球種","作戦","結果","打球","その他"]
    df_all = pd.DataFrame(all_data, columns=col)
    teams = df_all["攻撃"].unique() 
    teams =  [x for x in teams if pd.isnull(x) == False]
    selected_teams = st.multiselect("Team",teams)
    
    tab1, tab2 = st.tabs(["Pitcher", "Batter"])
    with tab1:
        df_t = df_all[~df_all["攻撃"].isin(selected_teams + [""])]
        pitchers = df_t["投手"].unique() 
        pitchers =  [x for x in pitchers if pd.isnull(x) == False]
        selected_pitchers = st.multiselect("Pitcher",pitchers)
        catchers = df_t["捕手"].unique()
        catchers =  [x for x in catchers if pd.isnull(x) == False]
        selected_catchers = st.multiselect("Catcher",catchers)
        df_p = df_t[df_t["投手"].isin(selected_pitchers)]
        df_pc = df_p[df_p["捕手"].isin(selected_catchers)]

        #書式の補正
        num1 = ["０","１","２","３","４","５","６","７","８","９"]
        num2 = ["0","1","2","3","4","5","6","7","8","9"]
        for x in range(10):
            number1 = num1[x]
            number2 = num2[x]
            df_pc["カウント"] = df_pc["カウント"].str.replace(number1, number2)
            df_pc["アウト"] = df_pc["アウト"].str.replace(number1, number2)
            df_pc["塁"] = df_pc["塁"].str.replace(number1, number2)
        df_pc["カウント"] = df_pc["カウント"].str.replace("・", "-")
        df_pc["球種"] = df_pc["球種"].str.replace("　", "")
        df_pc["塁"] = df_pc["塁"].str.replace("・", ",")
        df_pc["球種"] = df_pc["球種"].str.replace("チェンジアップ", "チェンジ")
        ####################################################################
        types_all = ["ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"]
        df_pc = df_pc[df_pc["球種"].isin(types_all)]
        df_pcr = df_pc[df_pc["打"].isin(["右"])]
        df_pcl = df_pc[df_pc["打"].isin(["左"])]

        R_list = []
        L_list = []
        counts = ["0-0","0-1","0-2","1-0","1-1","1-2","2-0","2-1","2-2","3-0","3-1","3-2"]
        #types = ["ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"]
        types = df_pc["球種"].unique() 
        types =  [x for x in types if pd.isnull(x) == False]

        for count in counts:
            r_list = []
            l_list = []
            df_pcrc = df_pcr[df_pcr["カウント"].isin([count])]
            df_pclc = df_pcl[df_pcl["カウント"].isin([count])]
            for type in types:
                df_pcrct = df_pcrc[df_pcrc["球種"].isin([type])]
                df_pclct = df_pclc[df_pclc["球種"].isin([type])]
                r_list.append(len(df_pcrct))
                l_list.append(len(df_pclct))
            R_list.append(r_list)
            L_list.append(l_list)
        
        df_R = pd.DataFrame(R_list, index=counts, columns=types)
        df_L = pd.DataFrame(L_list, index=counts, columns=types)
        
        #st.dataframe(df_pcr, 800, 400 )
        #st.dataframe(df_R, 800, 400 )
        #st.dataframe(df_pcl, 800, 400)
        #st.dataframe(df_L, 800, 400 )
        #fig = go.Figure()
        st.write("球種割合")
        if len(selected_pitchers) > 0:
            title_p = selected_pitchers[0]
        else:
            title_p = ""
        tab1a, tab1b = st.tabs(["対右", "対左"])
        with tab1a:
            fig = make_subplots(rows=4, cols=3,
                                specs=[[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}]],
                                subplot_titles=["対右 0-0","対右 0-1","対右 0-2","対右 1-0","対右 1-1","対右 1-2","対右 2-0","対右 2-1","対右 2-2","対右 3-0","対右 3-1","対右 3-2"])
            fig.add_trace(go.Pie(values = df_R.loc['0-0'],labels=types,textinfo='value'),row=1,col=1)
            fig.add_trace(go.Pie(values = df_R.loc['0-1'],labels=types,textinfo='value'),row=1,col=2)
            fig.add_trace(go.Pie(values = df_R.loc['0-2'],labels=types,textinfo='value'),row=1,col=3)
            fig.add_trace(go.Pie(values = df_R.loc['1-0'],labels=types,textinfo='value'),row=2,col=1)
            fig.add_trace(go.Pie(values = df_R.loc['1-1'],labels=types,textinfo='value'),row=2,col=2)
            fig.add_trace(go.Pie(values = df_R.loc['1-2'],labels=types,textinfo='value'),row=2,col=3)
            fig.add_trace(go.Pie(values = df_R.loc['2-0'],labels=types,textinfo='value'),row=3,col=1)
            fig.add_trace(go.Pie(values = df_R.loc['2-1'],labels=types,textinfo='value'),row=3,col=2)
            fig.add_trace(go.Pie(values = df_R.loc['2-2'],labels=types,textinfo='value'),row=3,col=3)
            fig.add_trace(go.Pie(values = df_R.loc['3-0'],labels=types,textinfo='value'),row=4,col=1)
            fig.add_trace(go.Pie(values = df_R.loc['3-1'],labels=types,textinfo='value'),row=4,col=2)
            fig.add_trace(go.Pie(values = df_R.loc['3-2'],labels=types,textinfo='value'),row=4,col=3)
            fig.update_layout(height=2000,title=title_p)
            st.plotly_chart(fig, use_container_width=False)
            st.dataframe(df_pcr, 800, 400 )

        with tab1b:

            fig2 = make_subplots(rows=4, cols=3,
                                specs=[[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}],[{"type": "domain"},{"type": "domain"},{"type": "domain"}]],
                                subplot_titles=["対左 0-0","対左 0-1","対左 0-2","対左 1-0","対左 1-1","対左 1-2","対左 2-0","対左 2-1","対左 2-2","対左 3-0","対左 3-1","対左 3-2"])
            fig2.add_trace(go.Pie(values = df_L.loc['0-0'],labels=types,textinfo='value'),row=1,col=1)
            fig2.add_trace(go.Pie(values = df_L.loc['0-1'],labels=types,textinfo='value'),row=1,col=2)
            fig2.add_trace(go.Pie(values = df_L.loc['0-2'],labels=types,textinfo='value'),row=1,col=3)
            fig2.add_trace(go.Pie(values = df_L.loc['1-0'],labels=types,textinfo='value'),row=2,col=1)
            fig2.add_trace(go.Pie(values = df_L.loc['1-1'],labels=types,textinfo='value'),row=2,col=2)
            fig2.add_trace(go.Pie(values = df_L.loc['1-2'],labels=types,textinfo='value'),row=2,col=3)
            fig2.add_trace(go.Pie(values = df_L.loc['2-0'],labels=types,textinfo='value'),row=3,col=1)
            fig2.add_trace(go.Pie(values = df_L.loc['2-1'],labels=types,textinfo='value'),row=3,col=2)
            fig2.add_trace(go.Pie(values = df_L.loc['2-2'],labels=types,textinfo='value'),row=3,col=3)
            fig2.add_trace(go.Pie(values = df_L.loc['3-0'],labels=types,textinfo='value'),row=4,col=1)
            fig2.add_trace(go.Pie(values = df_L.loc['3-1'],labels=types,textinfo='value'),row=4,col=2)
            fig2.add_trace(go.Pie(values = df_L.loc['3-2'],labels=types,textinfo='value'),row=4,col=3)
            fig2.update_layout(height=2000,title=title_p)
            st.plotly_chart(fig2, use_container_width=False)
            st.dataframe(df_pcl, 800, 400)

    with tab2:
        df_t2 = df_all[df_all["攻撃"].isin(selected_teams)]
        #書式の補正
        num1 = ["０","１","２","３","４","５","６","７","８","９"]
        num2 = ["0","1","2","3","4","5","6","7","8","9"]
        for x in range(10):
            number1 = num1[x]
            number2 = num2[x]
            df_t2["カウント"] = df_t2["カウント"].str.replace(number1, number2)
            df_t2["アウト"] = df_t2["アウト"].str.replace(number1, number2)
            df_t2["塁"] = df_t2["塁"].str.replace(number1, number2)
        df_t2["カウント"] = df_t2["カウント"].str.replace("・", "-")
        df_t2["球種"] = df_t2["球種"].str.replace("　", "")
        df_t2["塁"] = df_t2["塁"].str.replace("・", ",")
        df_t2["球種"] = df_t2["球種"].str.replace("チェンジアップ", "チェンジ")
        ####################################################################
        batters = df_t2["打者"].unique() 
        batters =  [x for x in batters if pd.isnull(x) == False]
        selected_batters = st.multiselect("Batter",batters)
        df_b = df_t2[df_t2["打者"].isin(selected_batters)]
        ####################################################################
        fast_ball = ["ストレート"]
        breaking_ball = ["スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"]
        all_ball = ["ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"]

        pichs = [fast_ball,breaking_ball,all_ball]
        results_swing = ["空振り","ファール","空振り三振","ゴロ","ライナー","フライ","振り逃げ","1BH","2BH","3BH","HR"]
        results_strike = ["見逃し","空振り","ファール","見逃し三振","空振り三振","ゴロ","ライナー","フライ","振り逃げ","1BH","2BH","3BH","HR"]
        result_list = [results_swing, results_strike ]

        PICH_list =[]
        for pich in pichs:
            for result in result_list:
                df_pich = df_b[df_b["球種"].str.contains("|".join(pich))]
                df_pich_result = df_pich[df_pich["結果"].str.contains("|".join(result))]
                pich_list = []
                for count in counts:
                    t = len(df_pich_result[df_pich_result["カウント"].isin([count])])
                    #print(df_pich_result[df_pich_result["カウント"].isin([count])])
                    pich_list.append(t)
                PICH_list.append(pich_list)

        index_swing_count = ["ストレート(スイング)","ストレート(ストライク)","変化球(スイング)","変化球(ストライク)","全球種(スイング)","全球種(ストライク)"]
        df_swing_count = pd.DataFrame(PICH_list, index=index_swing_count, columns=counts)

        types2 = ["ストレート","変化球","全球種"]

        RATIO_list = []
        for type2 in types2:
            ratio_list = []
            for count in counts:
                
                if df_swing_count.at[type2+"(ストライク)", count] != 0:
                    swing = df_swing_count.at[type2+"(スイング)", count]
                    strike = df_swing_count.at[type2+"(ストライク)", count]
                    ratio = str(int(100*swing/strike)) + "%  " + "(" + str(swing) + "/" + str(strike) +")"
                else:
                    ratio = ""
                ratio_list.append(ratio)
            RATIO_list.append(ratio_list)

        df_ratio = pd.DataFrame(RATIO_list, index=types2, columns=counts)
        df_ratio = df_ratio.T

        tab2a, tab2b = st.tabs(["打球方向","スイング率"])
        
        with tab2a:
            
            fig = go.Figure()
            x1 = [-70,0, 70]
            y1 = [70,0,70]
            fig.add_trace(go.Scatter(x=x1, y=y1, mode='lines',line=dict(color="black"))) 
            c1 = 50
            x2 = np.linspace(-66,66,200)
            y2 = (123-c1)*np.sqrt(1-((x2**2)/66**2)*(1-((66-c1)**2)/((123-c1)**2))) + c1
            fig.add_trace(go.Scatter(x=x2, y=y2, mode='lines',line=dict(color="black")))
            c2 = 20
            x3 = np.linspace(-27,27,200)
            y3 = np.sqrt(29**2 - x3**2) + 18
            fig.add_trace(go.Scatter(x=x3, y=y3, mode='lines',line=dict(color="black")))
            fig.add_trace(go.Scatter(x=[0], y=[38], mode='markers',marker=dict(color="black",symbol="diamond",size=7)))
            fig.add_trace(go.Scatter(x=[18], y=[20], mode='markers',marker=dict(color="black",symbol="diamond",size=7)))
            fig.add_trace(go.Scatter(x=[-18], y=[20], mode='markers',marker=dict(color="black",symbol="diamond",size=7)))
            fig.add_trace(go.Scatter(x=[55], y=[138], mode='markers+text',textposition="bottom center",text="球種：ストレート　　　",marker=dict(color="black",symbol="circle",size=10)))
            fig.add_trace(go.Scatter(x=[68], y=[138], mode='markers+text',textposition="bottom center",text="変化球",marker=dict(color="black",symbol="triangle-up",size=10)))
            fig.add_trace(go.Scatter(x=[50], y=[130], mode='markers+text',textposition="bottom center",text="構え：外　　　",marker=dict(color="orange",symbol="circle",size=10)))
            fig.add_trace(go.Scatter(x=[60], y=[130], mode='markers+text',textposition="bottom center",text="真ん中",marker=dict(color="forestgreen",symbol="circle",size=10)))
            fig.add_trace(go.Scatter(x=[70], y=[130], mode='markers+text',textposition="bottom center",text="内",marker=dict(color="royalblue",symbol="circle",size=10)))
            #####################################
            result_dakyu = ["ゴロ","ライナー","フライ","1BH","2BH","3BH","HR"]

            df_dakyu = df_b[df_b["結果"].str.contains("|".join(result_dakyu))]
            for i in range(len(df_dakyu)):
                dakyu_list1 = df_dakyu["打球"][i].split("(")
                if len(dakyu_list1) ==2:
                    dakyu_list2 = dakyu_list1[1].split(",")
                    dakyu_list2[1] = dakyu_list2[1].replace(")", "")
                    dakyu1 = int(dakyu_list2[0])  
                    dakyu2 = int(dakyu_list2[1])

                    if df_dakyu["球種"][i] == "ストレート":
                        symbol = "circle"
                    else:
                        symbol = "triangle-up"

                    if df_dakyu["構え"][i] == "外":
                        color = "orange"
                    elif df_dakyu["構え"][i] == "真ん中":
                        color = "forestgreen"
                    elif df_dakyu["構え"][i] == "内":
                        color = "royalblue"
                    else:
                        color = "black"

                    text = df_dakyu["球速"][i]

                    x4 = dakyu1*np.sin(np.pi*dakyu2/180)
                    y4 = dakyu1*np.cos(np.pi*dakyu2/180)

                    if x4 > 0:
                        x5 = np.linspace(0,x4,100)
                    else:
                        x5 = np.linspace(x4,0,100)
                    
                    dakyu_kekka = df_dakyu["結果"][i][:df_dakyu["結果"][i].find(" ")]
                    if dakyu_kekka == "ゴロ":
                        y5 = np.abs(4*np.sin(4*np.pi*x5/x4)) + y4*x5/x4
                    elif dakyu_kekka == "フライ":
                        x0 = (0.7)*x4
                        a = y4/((x4-x0)**2-x0**2)
                        y5 = a*(x5-x0)**2 - a*x0**2
                    else:
                        y5 = y4*x5/x4
                    
                    fig.add_trace(go.Scatter(x=x5, y=y5, mode='lines',line=dict(color=color,dash="solid",width=1)))
                    fig.add_trace(go.Scatter(x=[x4], y=[y4], mode='markers+text',textposition="top center",text=text,marker=dict(color=color,symbol=symbol,size=10)))

            ########################################
            fig.update_xaxes(showgrid=False,showticklabels=False)
            fig.update_yaxes(showgrid=False,showticklabels=False)
            if len(selected_batters) > 0:
                title_b = selected_batters[0]
            else:
                title_b = ""
            fig.update_layout( showlegend=False, xaxis=dict(range=(-75, 75)),yaxis=dict(range=(-10, 140)) ,width=700, height=800,title=title_b)
            st.plotly_chart(fig, use_container_width=False)
        
        with tab2b:
            st.dataframe(df_ratio,use_container_width= True)
