import streamlit as st
from groq import Groq
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - مساعد event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS لجعل الردود تبدو كبطاقات مزارع ---
st.markdown("""
    <style>
    .farm-card {
        background-color: #ffffff;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        margin: 10px 0px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stChatMessage { border-radius: 15px; }
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

# --- 3. الـ Prompt المعدل ليعطي رداً نصياً + JSON ---
system_prompt = f"""
أنت "ماكان"، المساعد الذكي لموقع event-jo.com. 
تحدث بلهجة أردنية ودودة ومحترفة.

البيانات: {json.dumps(farms_data)}

طريقة الرد الإلزامية:
1. ابدأ دائماً بجملة: "أبشر يا غالي، أكيد متوفر مزارع بـ [الموقع] بتناسبك."
2. لكل مزرعة تقترحها، اكتب المعلومات كالتالي:
   اسم المزرعة: [اسم المزرعة]
   موقعها: [الموقع]
   ليش اخترتلك إياها: [سبب بلهجة أردنية]
   السعر التقريبي: [السعر] دينار

3. في نهاية ردك تماماً، ضع الـ JSON التالي لغايات النظام:
{{
  "filters": {{"location": "", "price_range": "", "features": []}},
  "recommendations": [{{ "name": "", "id": "" }}]
}}
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد event-jo.com")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("مثلاً: بدي مزرعة بعمان"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # استخدام موديل Qwen على Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="qwen-2.5-32b", # تأكد من أن هذا الموديل متاح في حسابك
                temperature=0.6
            )
            
            full_response = chat_completion.choices[0].message.content
            
            # عرض الرد النصي الجميل للمستخدم
            if "{" in full_response:
                text_part = full_response.split("{")[0]
                st.markdown(text_part)
                
                # إظهار الـ JSON في مكان مخفي أو كـ Expander للفحص
                with st.expander("تفاصيل تقنية للبحث"):
                    json_part = "{" + full_response.split("{", 1)[1]
                    st.code(json_part, language='json')
            else:
                st.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
