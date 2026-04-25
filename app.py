import streamlit as st
from groq import Groq
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - مساعد event-jo.com الذكي", page_icon="🏡", layout="centered")

# --- تنسيق CSS لتحسين مظهر المحادثة ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stJson { background-color: #f8f9fa; border-radius: 10px; padding: 10px; border: 1px solid #ddd; }
    .stMarkdown h3 { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد المفتاح والبيانات ---
# ملاحظة: تأكد من حماية هذا المفتاح أو وضعه في Streamlit Secrets
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# بيانات المزارع (قاعدة البيانات المصغرة)
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

# --- 3. بناء تعليمات النظام (Prompt Engineering) ---
system_prompt = f"""
أنت "ماكان" (Makan)، المساعد الذكي الرسمي لموقع event-jo.com المتخصص في حجز مزارع الأردن.

شخصيتك:
- نشمي، محترف، وودود جداً.
- تتحدث بلهجة أردنية بيضاء وراقية.
- دائماً تفتخر بكونك جزءاً من فريق event-jo.com.

البيانات المتاحة لك: {json.dumps(farms_data)}

قواعد الرد:
1. إذا سألك المستخدم عن هويتك:
   - الرد: "أهلاً بك! أنا 'ماكان'، مساعدك الذكي من موقع event-jo.com. أنا هون لحتى أسهل عليك تلاقي أحلى مزارع الأردن اللي بتناسب جمعاتكم وذوقكم. كيف بقدر أخدمك اليوم؟"

2. عند طلب البحث عن مزارع:
   - ابدأ بترحيب حار وجملة تشويقية (مثلاً: "أبشر يا غالي، لقيتلك خيارات بتجنن بـ عمان...")
   - يجب أن يتبع النص JSON حصراً بالتنسيق التالي:
{{
  "filters": {{"location": "", "price_range": "", "features": []}},
  "assumptions": ["افتراضات ذكية بناءً على حاجة المستخدم"],
  "recommendations": [{{ "name": "", "reason": "اشرح الميزة بلهجة أردنية جذابة" }}]
}}

3. ملاحظات هامة:
   - لا تقترح مزارع غير متاحة (available: false).
   - إذا لم تجد طلباً مطابقاً تماماً، اقترح أقرب خيار واعتذر بلطف.
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 مساعد مزارع الأردن - ماكان")
st.caption("مرحباً بك في موقع event-jo.com - بوابتك لأجمل مزارع المملكة")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

# إدخال المستخدم
if prompt := st.chat_input("بدي مزرعة بالسلط فيها مسبح"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # الاتصال بـ Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            )
            
            full_response = chat_completion.choices[0].message.content
            
            # منطق فصل النص عن الـ JSON للعرض الجمالي
            if "{" in full_response and "}" in full_response:
                intro = full_response.split("{")[0].strip()
                json_string = "{" + full_response.split("{", 1)[1]
                
                if intro:
                    st.markdown(f"**ماكان:** {intro}")
                
                try:
                    # تنظيف الـ JSON من أي markdown tags
                    clean_json = json_string.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_json)
                    st.json(data)
                    st.session_state.messages.append({"role": "assistant", "content": data})
                except:
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
        except Exception as e:
            st.error(f"حدث خطأ في النظام: {e}")
