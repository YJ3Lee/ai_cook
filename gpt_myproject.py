import openai
import streamlit as st
from supabase import create_client
st.title("오늘 저녁 뭐 먹지? 🍽️")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url,key)


supabase = init_connection()
openai.api_key = st.secrets.OPENAI_TOKEN

def generate_prompt(person,menu_count, refrigerator,keywords,addr):
    prompt = f"""
오늘 저녁 메뉴를 {menu_count}가지로 짜 주세요. {person}명이 먹을 양입니다.
냉장고에는 {refrigerator}가 있습니다.
냉장고의 재료를 우선으로 이용할 수 있는 메뉴를 짜서 재료와 요리법과 실제 존재하는 요리 동영상 url도 써 주시고
냉장고의 재료가 없을 시에 {addr} 200M 이내의 마트를 검색하여 마트에서
사야할 품목과 품목의 양, 품목별 시세에 맞춘 예상금액,가까운 마트명, 금액 총합을 기록해 주세요

출력형식은
#★ 오늘의 저녁메뉴 :
#★ 가까운 마트:
#★ 사야할 품목(금액):
#★ 금액총합:

---
식사인원:{person}
메뉴 수:{menu_count}
냉장고재료:{refrigerator}
키워드:{keywords}
마트 :{addr}
---
"""
    return prompt.strip()

def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages=[
    {"role":"system","content":"당신은 현명한 주부입니다."},
    {"role":"user","content":prompt}
    ]
)
    return response["choices"][0]["message"]["content"]

def insert_database(person, menu_count,refrigerator, keywords, menu, buy_list,total_money,prompt):
    response = supabase.table("dinner_menu").insert({"person":person,
                                                     "menu_count":menu_count,
                                                     "keywords":keywords,
                                                     "refrigerator":refrigerator,
                                                     "menu":menu,
                                                     "buy_list":buy_list,
                                                     "total_money":total_money,
                                                     "prompt":prompt
                                                     }).execute()
    print(response)




def div_text(generated_text):

    list_text = generated_text.split("#")
    print(list_text)
    menu = list_text[1]
    buy_list = list_text[2] + list_text[3]
    total_money = list_text[4]
    return menu, buy_list, total_money

with st.form("my_form"):
    person = st.selectbox("식사인원",[2,3,4,5,6,7,8])
    menu_count = st.selectbox("반찬가지수",[3,4,5,6,7])
    refrigerator = st.text_input("냉장고 속 재료들:",placeholder="깍두기, 브로콜리, 냉동새우, 무, 파, 양파, 마늘, 계란, 다시멸치, 다시마,두부")
    addr = st.text_input("현재 위치")
    st.text("포함할 키워드(최대 3개까지 허용)")

    col1,col2,col3 = st.columns(3)
    with col1:
        keyword_one = st.text_input(placeholder="키워드 1",
                                    label="keyword_one",
                                    label_visibility="collapsed"
        )
    with col2:
        keyword_two = st.text_input(placeholder="키워드 2",
                                    label="keyword_two",
                                    label_visibility="collapsed"
        )
    with col3:
        keyword_three = st.text_input(placeholder="키워드 3",
                                    label="keyword_three",
                                    label_visibility="collapsed"
        )

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not person:
            st.error("식사인원을 선택하세요")
        if not menu_count:
            st.error("반찬가지수를 선택하세요")
        if not refrigerator:
            st.error("냉장고 속 재료를 써주세요")
        else:
            keywords = [keyword_one, keyword_two, keyword_three]
            keywords = [x for x in keywords if x]
            s_keywords = ",".join(keywords)

            prompt = generate_prompt(person,menu_count,refrigerator,keywords, addr)
            with st.spinner("AI 주부가 오늘 저녁 준비를 시작합니다..."):
                generated_text = request_chat_completion(prompt)
                menu, buy_list, total_money = div_text(generated_text)
                insert_database(person, menu_count, refrigerator, s_keywords, menu, buy_list, total_money,prompt)

                st.text_area(
                    label="오늘 저녁 메뉴",
                    value=menu,
                    height=300
                )
                st.text_area(
                    label="장보기 리스트",
                    value=buy_list,
                    height=200
                )
                st.text(total_money)
