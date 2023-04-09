
import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO

st.write("demo用")
# スプレッドシートの認証
scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'
]
credentials = service_account.Credentials.from_service_account_file( 'bbtapp230403-715595753eb1.json', scopes=scopes
)
gc = gspread.authorize(credentials)
# スプレッドシートからデータ取得
SP_SHEET_KEY = '1-yHFhguAZMcfVE12M95NHxKfEVgmhKYH4qO2Yrz3fLo'# スプレッドシートのキー
sh = gc.open_by_key(SP_SHEET_KEY)

SP_SHEET_KEY2 = '12MyuKNAo7vszl7qOti3mNwHLiymsNH4AghzT5Ge8D2c'# スプレッドシートのキー
sh2 = gc.open_by_key(SP_SHEET_KEY2)

SP_SHEET = 'シート1' # シート名「シート1」を指定
worksheet = sh.worksheet(SP_SHEET)
data = worksheet.get_all_values() # シート内の全データを取得
df = pd.DataFrame(data[1:], columns=data[0]) # 取得したデータをデータフレームに変換

def df_to_xlsx(df):
    byte_xlsx = BytesIO()
    writer_xlsx = pd.ExcelWriter(byte_xlsx, engine="xlsxwriter")
    df.to_excel(writer_xlsx, index=False, sheet_name="Sheet1")
    ##-----必要に応じてexcelのフォーマット等を設定-----##
    workbook = writer_xlsx.book
    worksheet = writer_xlsx.sheets["Sheet1"]
    format1 = workbook.add_format({"num_format": "0.00"})
    worksheet.set_column("A:A", None, format1)
    writer_xlsx.save()
    ##---------------------------------------------##
    workbook = writer_xlsx.book
    out_xlsx = byte_xlsx.getvalue()
    return out_xlsx


tab1, tab2,tab3, tab4 = st.tabs(["Input", "Data", "DataBase Uploader", "DataBase Editer"])


with tab1:
    with st.form("add_form",clear_on_submit=True):
        if len(df)<1:
            prev_row = ["1回表","","","","","","","0","","","","","","","","",]
        else:
            prev_row = df.iloc[-1]
        index = len(df) + 2
        pred_row = [""]*16
        prev_inning = prev_row[0]#回
        pred_inning1 = prev_inning.split("回")[0]
        if len(prev_row[0].split("回")) == 2:
            pred_inning2 = prev_inning.split("回")[1]
        else:
            pred_inning2 = ""
        pred_row[1] = prev_row[1]#攻撃
        pred_row[2] = prev_row[2]#投手
        pred_row[3] = prev_row[3]#捕手
        pred_row[4] = prev_row[4]#打者
        pred_row[5] = prev_row[5]#打
        pred_row[7] = prev_row[7]#塁
        prev_result1 = prev_row[13].split(" ")[0]
        if len(prev_row[13].split(" ")) == 2:
            prev_result2 = prev_row[13].split(" ")[1]
        else:
            prev_result2 = ""
        

        #predict
        if len(df)>0:
            if prev_row[8] == "":
                prev_ball = 0
                prev_strike = 0
            else:
                prev_BS = prev_row[8].split('-')
                prev_ball = int(prev_BS[0])
                prev_strike = int(prev_BS[1])

            def inning_change(df, prev_inning, pred_row):
                    pred_row[6] = "0" #アウト
                    pred_row[7] = "0" #塁
                    teams = df["攻撃"].unique() #攻撃
                    teams =  [x for x in teams if pd.isnull(x) == False]
                    if prev_inning.split("回")[1] == "表":
                        pred_inning1 = prev_inning.split("回")[0]
                        pred_inning2 = "裏"
                        if len(teams) == 2:
                            pred_row[1] = teams[-1] #攻撃
                            pitchers = df[df["攻撃"] == teams[-1]]["投手"].unique()
                            pitchers =  [x for x in pitchers if pd.isnull(x) == False]
                            pred_row[2] = pitchers[-1]
                            catchers = df[df["攻撃"] == teams[-1]]["捕手"].unique()
                            catchers =  [x for x in catchers if pd.isnull(x) == False]
                            pred_row[3] = catchers[-1]
                        else:
                            pred_row[1] = "" #攻撃
                            pred_row[2] = "" #投手
                            pred_row[3] = "" #捕手
                    else:
                        pred_inning1 = str(int(prev_inning.split("回")[0]) + 1)
                        pred_inning2 = "表"
                        if len(teams) == 2:
                            pred_row[1] = teams[0] #攻撃
                            pitchers = df[df["攻撃"] == teams[0]]["投手"].unique()
                            pitchers =  [x for x in pitchers if pd.isnull(x) == False]
                            pred_row[2] = pitchers[-1]
                            catchers = df[df["攻撃"] == teams[0]]["捕手"].unique()
                            catchers =  [x for x in catchers if pd.isnull(x) == False]
                            pred_row[3] = catchers[-1]
                        else:
                            pred_row[1] = "" #攻撃
                            pred_row[2] = "" #投手
                            pred_row[3] = "" #捕手
                    return pred_row, pred_inning1, pred_inning2

            if prev_result1 in ["ボール"]:
                pred_ball = prev_ball + 1
                pred_strike = prev_strike
                pred_row[6] = prev_row[6]#アウト
                
            elif prev_result1 in ["見逃し","空振り","ファール"]:
                if prev_strike < 2:
                    pred_ball = prev_ball
                    pred_strike = prev_strike + 1
                    pred_row[6] = prev_row[6]#アウト
                else:
                    pred_ball = prev_ball
                    pred_strike = prev_strike
                    pred_row[6] = prev_row[6]#アウト

            elif prev_result1 in ["見逃し三振","空振り三振","ゴロ","ライナー","フライ"] and prev_result2 != "エラー":
                pred_ball = 0
                pred_strike = 0
                pred_row[4] = "" #打者
                pred_row[5] = "" #打
                if int(prev_row[6]) < 2:
                    pred_row[6] = str(int(prev_row[6]) + 1 )#アウト
                else:
                    pred_row, pred_inning1, pred_inning2 = inning_change(df, prev_inning, pred_row)
                    

            elif prev_result1 in ["","牽制"]:
                pred_ball = prev_ball
                pred_strike = prev_strike
                pred_row[6] = prev_row[6]#アウト
            else:
                pred_ball = 0
                pred_strike = 0
                pred_row[6] = prev_row[6]#アウト
                pred_row[4] = "" #打者
                pred_row[5] = "" #打

##################################################################
            if prev_result2 == "ダブルプレー":
                pred_ball = 0
                pred_strike = 0
                pred_row[4] = "" #打者
                pred_row[5] = "" #打
                if int(pred_row[6]) < 2:
                    pred_row[6] = str(int(pred_row[6]) + 1 )#アウト
                elif int(pred_row[6]) == 2:
                    pred_row, pred_inning1, pred_inning2 = inning_change(df, prev_inning, pred_row)

            if prev_result2 == "トリプルプレー":
                pred_ball = 0
                pred_strike = 0
                pred_row[4] = "" #打者
                pred_row[5] = "" #打
                pred_row, pred_inning1, pred_inning2 = inning_change(df, prev_inning, pred_row)

            if prev_result2 == "ランナーアウト":
                if int(pred_row[6]) < 2:
                    pred_row[6] = str(int(pred_row[6]) + 1 )#アウト
                elif int(pred_row[6]) == 2:
                    pred_ball = 0
                    pred_strike = 0
                    pred_row[4] = "" #打者
                    pred_row[5] = "" #打
                    pred_row, pred_inning1, pred_inning2 = inning_change(df, prev_inning, pred_row)
###################################################################
        else:
            pred_ball = 0
            pred_strike = 0
            pred_row[6] = "0" #アウト

        new_row = [""] * 16

        col1a, col1b, col2, col3, col4 = st.columns((1,1,2,2,2))
        with col1a:
            inning1 = st.selectbox('回',(pred_inning1,"1","2","3","4","5","6","7","8","9","10","11","12"))
        with col1b:
            inning2 = st.selectbox(' ',(pred_inning2,"表","裏"))
        new_row[0] = inning1 + "回" +inning2
        with col2:
            new_row[1] = st.selectbox('攻撃',(pred_row[1],"福祉大","仙台大","学院大","東北大","工業大","宮教大"))
        with col3:
            new_row[2] = st.text_input('投手', pred_row[2])
        with col4:
            new_row[3] = st.text_input('捕手', pred_row[3])
        col5, col6, col7, col8, col9a,col9b = st.columns((2,1,1,2,1,1))
        with col5:
            new_row[4] = st.text_input('打者', pred_row[4])
        with col6:
            new_row[5] = st.selectbox("打",(pred_row[5],"右","左"))
        with col7:
            new_row[6] = st.selectbox("アウト",(pred_row[6],"0","1","2"))
        with col8:
            new_row[7] = st.selectbox("塁",(pred_row[7],"0","1","2","3","1,2","1,3","2,3","1,2,3"))
        with col9a:
            ball = st.selectbox("B",(str(pred_ball),"0","1","2","3"))
        with col9b:
            strike = st.selectbox("S",(str(pred_strike),"0","1","2"))
        new_row[8] = ball + "-" + strike
        col10, col11, col12, col13 = st.columns((1,1,1,1))
        with col10:
            new_row[9] = st.selectbox("構え",("","外","真ん中","内"))
        with col11:
            new_row[10] = st.text_input("球速","")
        with col12:
            new_row[11] = st.selectbox("球種",("","ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"))
        with col13:
            new_row[12] = st.selectbox("作戦",("","盗塁","ディレート","エンドラン","バント","セーフティ","スクイズ","セーフティスクイズ","バスター","バスターエンドラン","バントエンドラン"))
        col14a, col14b, col15, col16 = st.columns((1,1,1,1))
        with col14a:
            result1 = st.selectbox("結果",("","見逃し","空振り","ファール","ボール","見逃し三振","空振り三振","ゴロ","ライナー","フライ","振り逃げ","フォアボール","デッドボール","申告敬遠","1BH","2BH","3BH","HR","牽制"))
        if result1 == "牽制":
            new_row[10] = ""
        with col14b:
            result2 = st.selectbox("",(" ","エラー","ダブルプレー","トリプルプレー","ランナーアウト"))
        new_row[13] = result1 + " " +result2
        with col15:
            new_row[14] = st.selectbox("打球",("","1","2","3","4","5","6","7","8","9"))
        with col16:
            new_row[15] = st.text_input('備考',"")
        
        add = st.form_submit_button('ADD')

    with st.container():
        dakyu1 = st.slider("飛距離", 0, 130, 0)
        dakyu2 = st.slider("方向", -90, 90, 0)
        dakyu3 =  "(" + str(dakyu1) + "," + str(dakyu2) + ")"
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
        x4 = dakyu1*np.sin(np.pi*dakyu2/180)
        y4 = dakyu1*np.cos(np.pi*dakyu2/180)
        fig.add_trace(go.Scatter(x=[x4], y=[y4], mode='markers',marker=dict(color="orange",symbol="circle",size=10)))
        fig.update_xaxes(showgrid=False,showticklabels=False)
        fig.update_yaxes(showgrid=False,showticklabels=False)
        fig.update_layout( showlegend=False, xaxis=dict(range=(-70, 70)),yaxis=dict(range=(-10, 130)) ,width=600, height=700)
        st.plotly_chart(fig, use_container_width=True)
    if add:
        if new_row[14] != "":
            new_row[14] = new_row[14] + dakyu3
        worksheet.insert_row(new_row,index)
        st.experimental_rerun()
####################################################################################################################################
with tab2:
    xlsx_file = df_to_xlsx(df)
    import datetime
    dt_now = datetime.datetime.now()
    teams = df["攻撃"].unique() #攻撃
    teams =  [x for x in teams if pd.isnull(x) == False]
    if len(teams) ==2:
        team1 = teams[0]
        team2 = teams[1]
    elif len(teams)==1:
        team1 = teams[0]
        team2 = ""
    else:
        team1 = ""
        team2 = ""
    
    if len(str(dt_now.month)) == 1:
        month = "0" + str(dt_now.month)
    else:
        month = str(dt_now.month)

    if len(str(dt_now.day)) == 1:
        day = "0" + str(dt_now.day)
    else:
        day = str(dt_now.day)
    
    file_name = str(dt_now.year) + "_" + month + "_" + day + "_" + team1 + "_" + team2
    coldownload, coldatabase, colspace1 = st.columns((1,1,1))
    with coldownload:
        st.download_button(label="Download", data=xlsx_file, file_name= file_name + ".xlsx")
    with coldatabase:
        if st. button("Save to DataBase"):
            ws_list = sh2.worksheets()
            ws_name_list = []
            for i  in range(len(sh2.worksheets())):
                ws_name_list.append(ws_list[i].title)
            df = df.fillna("")
            df_list = df.to_numpy().tolist()
            label = ["回","攻撃","投手","捕手","打者","打","アウト","塁","B/S","構え","球速","球種","作戦","結果","打球","その他"]
            if file_name not in ws_name_list:     
                ws = sh2.add_worksheet(file_name, rows=1000, cols=30)
                ws.clear()
                ws.insert_row(label,1)
                ws.append_rows(df_list)
            else:
                ws = sh2.worksheet(file_name)
                ws.clear()
                ws.insert_row(label,1)
                ws.append_rows(df_list)

    with st.sidebar:
        if st.button('Clear All Data'):
            #st.write("Are you sure you want to permanently delete all data ?")
            label = ["回","攻撃","投手","捕手","打者","打","アウト","塁","B/S","構え","球速","球種","作戦","結果","打球","その他"]
            worksheet.clear()
            worksheet.insert_row(label,1)
            st.experimental_rerun()

    st.dataframe(df, 800, 400 )
    index_list = [""] + list(range(0,len(df)))
    selected_row_index = st.selectbox("row index",(index_list))


    if selected_row_index != "":        
        colDEL, colINSERT, colspace = st.columns((1,1,4))

        with colDEL:
            if st.button ("Delete"):
                worksheet.delete_rows(selected_row_index+2)
                st.experimental_rerun()

        with colINSERT:
            if st.button ("Insert"):
                prev_list = df[selected_row_index:selected_row_index+1].values.tolist()[0]
                next_list = prev_list[0:9] + ["","","","","","",""]
                worksheet.insert_row(next_list, selected_row_index+3)
                st.experimental_rerun()

#########FORM######################
        with st.form("edit_form",clear_on_submit=True):
            edit_list = [""]*16
            prev_list = df[selected_row_index:selected_row_index+1].values.tolist()[0]
            prev_inn1 = prev_list[0].split("回")[0]
            if len(prev_list[0].split("回")) == 2:
                prev_inn2 = prev_list[0].split("回")[1]
            else:
                prev_inn2 = ""

            if prev_list[8] == "":
                prev_b = "0"
                prev_s = "0"
            else:
                prev_bs = prev_list[8].split('-')
                prev_b = prev_bs[0]
                prev_s = prev_bs[1]

            prev_resulta = prev_list[13].split(" ")[0]
            if len(prev_list[13].split(" ")) == 2:
                prev_resultb = prev_list[13].split(" ")[1]
            else:
                prev_resultb = ""

            if prev_list[14] != "":
                prev_dakyu = prev_list[14].split("(")
                prev_dakyu1 = prev_dakyu[0]
                if prev_dakyu[1] != "":
                    prev_dakyu2 = prev_dakyu[1].split(",")
                    prev_dakyu2[1] = prev_dakyu2[1].replace(")", "")
                
            
            col1a, col1b, col2, col3, col4 = st.columns((1,1,2,2,2))
            with col1a:
                edit_inning1 = st.selectbox('回',(prev_inn1,"1","2","3","4","5","6","7","8","9","10","11","12"))
            with col1b:
                edit_inning2 = st.selectbox(' ',(prev_inn2,"表","裏"))
            edit_list[0] = edit_inning1 + "回" + edit_inning2
            with col2:
                edit_list[1] = st.selectbox('攻撃',(prev_list[1],"福祉大","仙台大","学院大","東北大","工業大","宮教大"))
            with col3:
                edit_list[2] = st.text_input('投手', prev_list[2])
            with col4:
                edit_list[3] = st.text_input('捕手', prev_list[3])
            col5, col6, col7, col8, col9a,col9b = st.columns((2,1,1,2,1,1))
            with col5:
                edit_list[4] = st.text_input('打者', prev_list[4])
            with col6:
                edit_list[5] = st.selectbox("打",(prev_list[5],"右","左"))
            with col7:
                edit_list[6] = st.selectbox("アウト",(prev_list[6],"0","1","2"))
            with col8:
                edit_list[7] = st.selectbox("塁",(prev_list[7],"0","1","2","3","1,2","1,3","2,3","1,2,3"))
            with col9a:
                ball = st.selectbox("B",(prev_b,"0","1","2","3"))
            with col9b:
                strike = st.selectbox("S",(prev_s,"0","1","2"))
            edit_list[8] = ball + "-" + strike
            col10, col11, col12, col13 = st.columns((1,1,1,1))
            with col10:
                edit_list[9] = st.selectbox("構え",(prev_list[9],"外","真ん中","内"))
            with col11:
                edit_list[10] = st.text_input("球速",prev_list[10])
            with col12:
                edit_list[11] = st.selectbox("球種",(prev_list[11],"ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"))
            with col13:
                edit_list[12] = st.selectbox("作戦",(prev_list[12],"盗塁","ディレート","エンドラン","バント","セーフティ","スクイズ","セーフティスクイズ","バスター","バスターエンドラン","バントエンドラン"))
            col14a, col14b, col15, col16 = st.columns((1,1,1,1))
            with col14a:
                resulta = st.selectbox("結果",(prev_resulta,"","見逃し","空振り","ファール","ボール","見逃し三振","空振り三振","ゴロ","ライナー","フライ","振り逃げ","フォアボール","デッドボール","申告敬遠","1BH","2BH","3BH","HR","牽制"))
            if resulta == "牽制":
                edit_list[10] = ""
            with col14b:
                resultb = st.selectbox(" ",(prev_resultb,"","エラー","ダブルプレー","トリプルプレー","ランナーアウト"))
            edit_list[13] = resulta + " " +resultb
            with col15:
                edit_list[14] = st.selectbox("打球",(prev_dakyu1,"","1","2","3","4","5","6","7","8","9"))
            with col16:
                edit_list[15] = st.text_input('備考',prev_list[15])

            edit = st.form_submit_button('Edit')
        with st.container():
            dakyu4 = st.slider("飛距離", 0, 130, int(prev_dakyu2[0]))
            dakyu5 = st.slider("方向", -90, 90, int(prev_dakyu2[1]))
            dakyu6 =  "(" + str(dakyu4) + "," + str(dakyu5) + ")"
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
            x4 = dakyu4*np.sin(np.pi*dakyu5/180)
            y4 = dakyu4*np.cos(np.pi*dakyu5/180)
            fig.add_trace(go.Scatter(x=[x4], y=[y4], mode='markers',marker=dict(color="orange",symbol="circle",size=10)))
            fig.update_xaxes(showgrid=False,showticklabels=False)
            fig.update_yaxes(showgrid=False,showticklabels=False)
            fig.update_layout( showlegend=False, xaxis=dict(range=(-70, 70)),yaxis=dict(range=(-10, 130)) ,width=600, height=700)
            st.plotly_chart(fig, use_container_width=True)

        if edit:
            if edit_list[14] != "":
                edit_list[14] = edit_list[14] + dakyu6
            worksheet.insert_row(edit_list, selected_row_index+3)
            worksheet.delete_rows(selected_row_index+2)
            st.write("edited")
            st.experimental_rerun()

#####################################################################################################################################################
with tab3:
    uploaded_files = st.file_uploader("xlsx file upload", type='xlsx',accept_multiple_files=True)
    if uploaded_files is not None:
        if st.button("Upload"):
            for uploaded_file in uploaded_files:
                #print("uploaded")
                uploaded_file_name = str(uploaded_file.name)
                new_sheet_name = uploaded_file_name.replace(".xlsx","")
                ws_list = sh2.worksheets()
                ws_name_list = []
                for i  in range(len(sh2.worksheets())):
                    ws_name_list.append(ws_list[i].title)
                #print(uploaded_file_name)
                #print(ws_name_list)
                if new_sheet_name not in ws_name_list:
                    df_data = pd.read_excel(uploaded_file)
                    df_data = df_data.fillna("")
                    data_list = df_data.to_numpy().tolist()
                    
                    label = ["回","攻撃","投手","捕手","打者","打","アウト","塁","B/S","構え","球速","球種","作戦","結果","打球","その他"]
                    
                    ws = sh2.add_worksheet(new_sheet_name, rows=1000, cols=30)
                    ws.clear()
                    ws.insert_row(label,1)
                    ws.append_rows(data_list)
                    st.write(new_sheet_name + "  added")
                else:
                    st.write(new_sheet_name + "  already exists")
    ws_list = sh2.worksheets()
    ws_name_list = []
    for i  in range(len(sh2.worksheets())):
        ws_name_list.append(ws_list[i].title)
    game_list = ws_name_list[1:]
    selected_games = st.multiselect("select games",game_list)

    if selected_games is not None:
        if st.button("Remove"):
            for game in selected_games:
                remove_ws = sh2.worksheet(game)
                sh2.del_worksheet(remove_ws)
        
        for game in selected_games:
            DL_ws = sh2.worksheet(game)
            DL_data = DL_ws.get_all_values() # シート内の全データを取得
            df_DL = pd.DataFrame(DL_data[1:], columns=DL_data[0]) # 取得したデータをデータフレームに変換
            dl_xlsx_file = df_to_xlsx(df_DL)
            st.download_button(label="Download  " + game, data=dl_xlsx_file, file_name= game + ".xlsx")

with tab4:
    ws_list2 = sh2.worksheets()
    ws_name_list2 = []
    for i  in range(len(sh2.worksheets())):
        ws_name_list2.append(ws_list2[i].title)
    game_list2 = ws_name_list2[1:]
    selected_game = st.selectbox("select game",[""] + game_list2)
    
    if selected_game != "":
        edit_ws = sh2.worksheet(selected_game)
        edit_data = edit_ws.get_all_values() # シート内の全データを取得
        df_edit = pd.DataFrame(edit_data[1:], columns=edit_data[0]) # 取得したデータをデータフレームに変換

        col_rename_exp,col_rename_space = st.columns((2,1))
        with col_rename_exp:
            with st.expander("Rename"):

                col_newname, col_rename = st.columns((3,1))

                with col_newname:
                    st_name = st.text_input("new name",selected_game,label_visibility="collapsed")
                with col_rename:
                    if st.button("Rename"):
                        try:
                            edit_ws.update_title(st_name)
                            st.experimental_rerun()
                        except Exception as e:
                            edit_ws.write("failed")

        st.dataframe(df_edit, 800, 400 )
        index_list2 = [""] + list(range(0,len(df_edit)))
        selected_row_index2 = st.selectbox("row index",(index_list2))

        if selected_row_index2 != "":
            with st.form("edit_form",clear_on_submit=True):
                edit2_list = [""]*16
                prev2_list = df_edit[selected_row_index2:selected_row_index2+1].values.tolist()[0]
                prev2_inn1 = prev2_list[0].split("回")[0]
                if len(prev2_list[0].split("回")) == 2:
                    prev2_inn2 = prev2_list[0].split("回")[1]
                else:
                    prev2_inn2 = ""

                if prev2_list[8] == "":
                    prev2_b = "0"
                    prev2_s = "0"
                else:
                    prev2_bs = prev2_list[8].split('-')
                    prev2_b = prev2_bs[0]
                    prev2_s = prev2_bs[1]

                prev2_resulta = prev2_list[13].split(" ")[0]
                if len(prev2_list[13].split(" ")) == 2:
                    prev2_resultb = prev2_list[13].split(" ")[1]
                else:
                    prev2_resultb = ""

                if prev2_list[14] != "":
                    prev2_dakyu = prev2_list[14].split("(")
                    prev2_dakyu1 = prev2_dakyu[0]
                    if prev2_dakyu[1] != "":
                        prev2_dakyu2 = prev2_dakyu[1].split(",")
                        prev2_dakyu2[1] = prev2_dakyu2[1].replace(")", "")
                    
                
                col1a, col1b, col2, col3, col4 = st.columns((1,1,2,2,2))
                with col1a:
                    edit2_inning1 = st.selectbox('回',(prev2_inn1,"1","2","3","4","5","6","7","8","9","10","11","12"))
                with col1b:
                    edit2_inning2 = st.selectbox(' ',(prev2_inn2,"表","裏"))
                edit2_list[0] = edit2_inning1 + "回" + edit2_inning2
                with col2:
                    edit2_list[1] = st.selectbox('攻撃',(prev2_list[1],"福祉大","仙台大","学院大","東北大","工業大","宮教大"))
                with col3:
                    edit2_list[2] = st.text_input('投手', prev2_list[2])
                with col4:
                    edit2_list[3] = st.text_input('捕手', prev2_list[3])
                col5, col6, col7, col8, col9a,col9b = st.columns((2,1,1,2,1,1))
                with col5:
                    edit2_list[4] = st.text_input('打者', prev2_list[4])
                with col6:
                    edit2_list[5] = st.selectbox("打",(prev2_list[5],"右","左"))
                with col7:
                    edit2_list[6] = st.selectbox("アウト",(prev2_list[6],"0","1","2"))
                with col8:
                    edit2_list[7] = st.selectbox("塁",(prev2_list[7],"0","1","2","3","1,2","1,3","2,3","1,2,3"))
                with col9a:
                    ball = st.selectbox("B",(prev2_b,"0","1","2","3"))
                with col9b:
                    strike = st.selectbox("S",(prev2_s,"0","1","2"))
                edit2_list[8] = ball + "-" + strike
                col10, col11, col12, col13 = st.columns((1,1,1,1))
                with col10:
                    edit2_list[9] = st.selectbox("構え",(prev2_list[9],"外","真ん中","内"))
                with col11:
                    edit2_list[10] = st.text_input("球速",prev2_list[10])
                with col12:
                    edit2_list[11] = st.selectbox("球種",(prev2_list[11],"ストレート","スライダー","カーブ","フォーク","チェンジ","シュート","カット","ツーシーム","シンカー"))
                with col13:
                    edit2_list[12] = st.selectbox("作戦",(prev2_list[12],"盗塁","ディレート","エンドラン","バント","セーフティ","スクイズ","セーフティスクイズ","バスター","バスターエンドラン","バントエンドラン"))
                col14a, col14b, col15, col16 = st.columns((1,1,1,1))
                with col14a:
                    resulta = st.selectbox("結果",(prev2_resulta,"","見逃し","空振り","ファール","ボール","見逃し三振","空振り三振","ゴロ","ライナー","フライ","振り逃げ","フォアボール","デッドボール","申告敬遠","1BH","2BH","3BH","HR","牽制"))
                if resulta == "牽制":
                    edit2_list[10] = ""
                with col14b:
                    resultb = st.selectbox(" ",(prev2_resultb,"","エラー","ダブルプレー","トリプルプレー","ランナーアウト"))
                edit2_list[13] = resulta + " " +resultb
                with col15:
                    edit2_list[14] = st.selectbox("打球",(prev2_dakyu1,"","1","2","3","4","5","6","7","8","9"))
                with col16:
                    edit2_list[15] = st.text_input('備考',prev2_list[15])

                edit2 = st.form_submit_button('Edit')
            with st.container():
                dakyu7 = st.slider("飛距離", 0, 130, int(prev2_dakyu2[0]))
                dakyu8 = st.slider("方向", -90, 90, int(prev2_dakyu2[1]))
                dakyu9 =  "(" + str(dakyu7) + "," + str(dakyu8) + ")"
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
                x4 = dakyu7*np.sin(np.pi*dakyu8/180)
                y4 = dakyu7*np.cos(np.pi*dakyu8/180)
                fig.add_trace(go.Scatter(x=[x4], y=[y4], mode='markers',marker=dict(color="orange",symbol="circle",size=10)))
                fig.update_xaxes(showgrid=False,showticklabels=False)
                fig.update_yaxes(showgrid=False,showticklabels=False)
                fig.update_layout( showlegend=False, xaxis=dict(range=(-70, 70)),yaxis=dict(range=(-10, 130)) ,width=600, height=700)
                st.plotly_chart(fig, use_container_width=True)

            if edit2:
                if edit2_list[14] != "":
                    edit2_list[14] = edit2_list[14] + dakyu9
                edit_ws.insert_row(edit2_list, selected_row_index2+3)
                edit_ws.delete_rows(selected_row_index2+2)
                st.write("edited")
                st.experimental_rerun()
