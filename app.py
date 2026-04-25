import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS احترافي ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .farm-card {
        background-color: #f9f9f9;
        border-right: 6px solid #2e7d32;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        direction: rtl;
    }
    .farm-name { color: #2e7d32; font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
    .farm-detail { color: #333; font-size: 1rem; margin-bottom: 3px; }
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

# --- 3. البرومبت الاحترافي ---
system_prompt = f"""
أنت المساعد الذكي "ماكان" لموقع event-jo.com. 
مهمتك مساعدة الأردنيين في حجز مزارع من هذه البيانات: {json.dumps(farms_data)}

شروط الرد الإلزامية:
1. ابدأ دائماً بجملة ترحيبية أردنية (مثال: "يا هلا والله، أبشر من عيوني...")
2. اذكر أسماء المزارع المقترحة باختصار في النص.
3. ضع تفاصيل البحث التقنية في نهاية الرد داخل وسم [DATA]...[/DATA] بصيغة JSON حصراً.
4. التنسيق المطلوب للـ JSON:
   {{"recommendations": [{{"name": "", "price": "", "features": "", "reason": ""}}]}}
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("موقع event-jo.com يرحب بك")

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

            # --- منطق الاستخراج الذكي ---
            # البحث عن الـ JSON داخل الوسوم [DATA]
            json_match = re.search(r"\[DATA\](.*?)\[/DATA\]", full_response, re.DOTALL)
            
            # عرض النص (كل شيء قبل الوسم)
            display_text = full_response.split("[DATA]")[0].strip()
            st.markdown(f"### ✨ رد ماكان:")
            st.write(display_text)

            if json_match:
                try:
                    json_str = json_match.group(1).strip()
                    data = json.loads(json_str)
                    
                    st.markdown("---")
                    for rec in data.get("recommendations", []):
                        st.markdown(f"""
                        <div class="farm-card">
                            <div class="farm-name">🏠 {rec['name']}</div>
                            <div class="farm-detail">💰 السعر: {rec.get('price', 'حسب التواصل')} دينار</div>
                            <div class="farm-detail">🌟 المميزات: {rec.get('features', 'مسبح وجلسات')}</div>
                            <div class="farm-detail">📝 ليش بنصحك فيها: {rec.get('reason', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    pass # إذا فشل الـ JSON ما بنخرب الواجهة
            
            st.session_state.messages.append({"role": "assistant", "content": display_text})
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
