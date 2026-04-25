import streamlit as st
from groq import Groq
import json

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مساعد مزارع الأردن (Groq)", page_icon="⚡", layout="centered")

# --- تنسيق CSS ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stJson { background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. إعداد المفتاح والبيانات ---
# الـ API Key اللي زودتني فيه
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

# --- 2. بناء تعليمات النظام ---
system_prompt = f"""
أنت مساعد ذكي لمنصة حجز مزارع في الأردن. 
داتا المزارع المتاحة: {json.dumps(farms_data)}

المهام:
- للأسئلة العامة: جاوب بلهجة أردنية ودودة.
- لطلبات البحث: أعطِ النتيجة حصراً بصيغة JSON التالية:
{{
  "filters": {{"location": "", "price_range": "", "features": []}},
  "assumptions": ["افتراضاتك"],
  "recommendations": [{{"name": "", "reason": ""}}]
}}
قاعدة: لا تقترح أي مزرعة available: false.
"""

# --- 3. واجهة المستخدم ---
st.title("🏡 بوكر مزارع الأردن (Powered by Groq)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("بدي مزرعة بعمان فيها مسبح"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # طلب الرد من Groq (استخدام موديل llama-3.3-70b-versatile هو الأفضل حالياً)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            text_resp = chat_completion.choices[0].message.content
            
            try:
                # استخراج الـ JSON
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
            st.error(f"حدث خطأ: {e}")
