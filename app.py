import streamlit as st
import google.generativeai as genai
import json

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="مساعد حجز مزارع الأردن", page_icon="🏡", layout="centered")

st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stJson { background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد المفتاح والبيانات ---
# ضع مفتاحك هنا (تأكد أنه يبدأ بـ AIza)
API_KEY = "AIzaSyDkwqVEQroepg-R1Mxeml1bmGzjX9oQnQw" 
genai.configure(api_key=API_KEY)

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

# --- 3. بناء الموديل مع معالجة خطأ 404 ---
system_instruction = f"أنت مساعد ذكي لمنصة حجز مزارع في الأردن. داتا المزارع المتاحة: {json.dumps(farms_data)}. المهام: للأسئلة العامة جاوب بلهجة أردنية. لطلبات البحث أعطِ النتيجة حصراً بصيغة JSON فيها filters و assumptions و recommendations."

# محاولة تحميل الموديل بأكثر من اسم لضمان التوافق
model_names = ["gemini-1.5-flash-latest", "models/gemini-1.5-flash", "gemini-1.5-flash", "gemini-1.0-pro"]
model = None

for name in model_names:
    try:
        model = genai.GenerativeModel(model_name=name, system_instruction=system_instruction)
        # تجربة بسيطة للتأكد أن الموديل شغال
        model.generate_content("test") 
        break 
    except Exception:
        continue

if model is None:
    st.error("عذراً، فشل الاتصال بكافة إصدارات الموديل. تأكد من الـ API Key وإصدار المكتبة.")

# --- 4. واجهة المستخدم ---
st.title("🏡 بوكر مزارع الأردن")
st.caption("أهلاً بك في نظام البحث الذكي")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("بدي مزرعة في جرش فيها مسبح"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model:
            try:
                response = model.generate_content(prompt)
                text_resp = response.text
                try:
                    # محاولة استخراج JSON من الرد
                    clean_json = text_resp.strip()
                    if "```json" in clean_json:
                        clean_json = clean_json.split("```json")[1].split("```")[0]
                    elif "```" in clean_json:
                        clean_json = clean_json.split("```")[1].split("```")[0]
                    
                    data = json.loads(clean_json.strip())
                    st.json(data)
                    st.session_state.messages.append({"role": "assistant", "content": data})
                except:
                    st.markdown(text_resp)
                    st.session_state.messages.append({"role": "assistant", "content": text_resp})
            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد الرد: {e}")
