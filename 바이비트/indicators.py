import pandas as pd
def ma( data, w):
    """
    이동평균선 

    df :  캔들 데이터
    w : 주기 
    """
    return data.rolling(w).mean()

def Bollinger_Band(df,w,k=2):
    # 중심선 (MIDDLE) : n일 이동평균선
    df["middle"]=df['close'].rolling(w).mean()
    df["MA20_std"]=df['close'].rolling(w).std()
    std = pd.DataFrame(df["MA20_std"])
    sem = std.sem() # 표준 오차
    # print(sem)
    #상한선 (UPPER) : 중심선 + (표준편차 × K)
    #하한선 (LOWER) : 중심선 - (표준편차 × K)
    df["upper"]=df.apply(lambda x: x["middle"]+k*x["MA20_std"],1)
    df["lower"]=df.apply(lambda x: x["middle"]-k*x["MA20_std"],1)
    df['pb'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])

    bb = df[['upper','middle','lower','pb']]
    return bb