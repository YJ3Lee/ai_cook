import datetime

import streamlit as st
import openai
from supabase import create_client

@st.cache_resource
def init_database():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url,key)

supabase = init_database()
openai.api_key = st.secrets.OPENAI_TOKEN

def insert_database(weather, who, person, favor,result,prompt):
    response =supabase.table("snack").insert({"weather":weather,
                                    "who":who,
                                    "person":person,
                                    "favor":favor,
                                    "result":result,
                                    "prompt":prompt
                                    }).execute()
    print(response)


def make_prompt(t_day,weather,who,person,favor):
    prompt_text = f"""
오늘은 {t_day}이고 날씨는 {weather}. 이런날 {who}가 {person}명 먹을 간식을 제시해주세요.
간식은 {favor} 좋아합니다.
인스턴트가 아니면서 한국 재료로 간단하게 만들 수 있는 맛있는 간식을 앓려주세요.
---
오늘 :{t_day}
날씨 :{weather}
대상 :{who}
인원 :{person}
취향 :{favor}
---

"""
    return prompt_text.strip()

def response_gpt(prompt):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role":"system","content":"당신은 간식전문가입니다."},
            {"role":"user","content":prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]


st.title("오늘의 간식은?🍩")

t_day = datetime.date.today()
st.text(t_day)
with st.form("today_snack"):
    weather = st.text_input("오늘의 날씨는?", placeholder="매우 덥다")
    col1, col2, col3 = st.columns(3)
    with col1:
        who= st.text_input("대상",placeholder = "초등,중등,어른")
    with col2:
        person= st.selectbox("인원",[1,2,3,4,5])
    with col3:
        favor= st.text_input("취향")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not weather:
        st.error("오늘의 날씨를 입력해주세요")
    if not who:
        st.error("간식을 먹을 대상을 입력해주세요.")
    if not person:
        st.error("간식을 먹을 인원을 입력해주세요.")
    if not favor:
        st.error("취향을 입력해주세요")
    else:
        prompt=make_prompt(t_day,weather,who,person,favor)
        result = response_gpt(prompt)
        insert_database(weather, who, person, favor, result, prompt)
        with st.spinner("AI 엄마가 간식을 준비합니다...."):
            st.text_area(
                label = "간식 준비 완료",
                value = result,
                height=500
            )