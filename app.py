import streamlit as st
from groq import Groq
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - مساعد event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS لتحسين العرض البصري ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .farm-card {
        background-color: #ffffff;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .farm-name { color: #2e7d32; font-size: 20px; font-weight: bold; }
    .farm-reason { color: #555; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد المفتاح والبيانات ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

farms_data = [
    {"id": 1, "name": "Green Valley Farm", "location": "Amman", "price_per_day": 120, "available": True, "features": ["Pool", "BBQ", "WiFi"]},
    {"id": 2, "name": "Sunset Farm", "location": "Salt", "price_per_day": 90, "available": True, "features": ["BBQ", "Garden"]},
    {"id": 3, "name": "Olive Tree Farm", "location": "Jerash", "price_per_day": 110, "available": False, "features": ["Pool", "BBQ"]},
    {"id": 4, "name": "Blue Sky Farm", "location": "Madaba", "price_per_day": 100, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 5, "name": "Golden Field Farm", "location": "Irbid", "price_per_day": 95, "available": True, "features": ["Parking", "Farm Animals"]},
    {"id": 6, "name": "Royal Hills Farm", "location": "Amman", "price_per_day": 150, "available": True, "features": ["Pool", "Luxury Seating"]},
    {"id": 7, "name": "Cherry Blossom Farm", "location": "Ajloun", "price_per_day": 85, "available": True, "features": ["Nature View", "BBQ"]},
    {"id": 8, "name": "Palm Oasis Farm", "location": "Aqaba", "price_per_day": 140, "available": False, "features": ["Pool", "Sea View"]},
    {"id": 9, "name": "Green Haven Farm", "location": "Zarqa", "price_per_day": 80, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 10, "name": "Desert Rose Farm", "location": "Wadi Rum", "price_per_day": 160, "available": True, "features": ["Luxury Tents", "Campfire"]},
    {"id": 11, "name": "Farm 11", "location": "Amman", "price_per_day": 105, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 12, "name": "Farm 12", "location": "Salt", "price_per_day": 92, "available": True, "features": ["Garden", "BBQ"]},
    {"id": 13, "name": "Farm 13", "location": "Jerash", "price_per_day": 115, "available": False, "features": ["Pool", "Playground"]},
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 3. تعليمات النظام ---
system_prompt = f"""
أنت "ماكان" (Makan)، المساعد الذكي لموقع event-jo.com.
مهمتك مساعدة المستخدمين في العثور على مزارع في الأردن من هذه الداتا: {json.dumps(farms_data)}

شخصيتك: أردني نشمي، ودود، ومهني.

عند طلب مزرعة، يجب أن ترد بنص طبيعي أولاً، متبوعاً بـ JSON يحتوي على التفاصيل. 
تأكد أن الـ JSON نظيف تماماً ولا يحتوي على ترقيم خارجي (مثل 0: أو 1:).
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد حجز مزارع الأردن")
st.caption("خدمة ذكية مقدمة من event-jo.com")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("بدي مزرعة بعمان"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.6,
            )
            full_response = chat_completion.choices[0].message.content

            if "{" in full_response:
                intro = full_response.split("{")[0].strip()
                json_part = "{" + full_response.split("{", 1)[1]
                
                # عرض الترحيب
                if intro:
                    st.markdown(f"### ✨ أبشر، هاي أحلى مزارع طلبك:")
                    st.write(intro)
                
                try:
                    # تنظيف وتحويل الـ JSON
                    clean_json = json_part.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    
                    # عرض المزارع بتنسيق فخم (Cards)
                    for rec in data.get("recommendations", []):
                        st.markdown(f"""
                        <div class="farm-card">
                            <div class="farm-name">📍 الاسم: {rec['name']}</div>
                            <div class="farm-reason">💡 المميزات: {rec['reason']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with st.expander("بيانات النظام التقنية"):
                        st.json(data)
                except:
                    st.markdown(full_response)
            else:
                st.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"عذراً، حدث خطأ: {e}")
