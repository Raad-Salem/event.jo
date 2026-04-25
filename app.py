import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS ثابت ونظيف ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    .farm-card {
        background-color: #ffffff;
        border-right: 6px solid #2e7d32;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 15px 0;
        direction: rtl;
        text-align: right;
    }
    .farm-name { color: #2e7d32; font-size: 1.3rem; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .farm-info { color: #333; font-size: 1rem; line-height: 1.7; margin-bottom: 4px; }
    .farm-info b { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات والـ API ---
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
    {"id": 9, "name": "Green Haven Farm", "location": "Zarqa", "price_per_day": 80, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 10, "name": "Desert Rose Farm", "location": "Wadi Rum", "price_per_day": 160, "available": True, "features": ["Luxury Tents", "Campfire"]},
    {"id": 11, "name": "Farm 11", "location": "Amman", "price_per_day": 105, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 12, "name": "Farm 12", "location": "Salt", "price_per_day": 92, "available": True, "features": ["Garden", "BBQ"]},
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 3. البرومبت "الصارم" ---
system_prompt = f"""
أنت المساعد "ماكان" من event-jo.com. 
مهمتك الوحيدة هي ترشيح مزارع من القائمة التالية: {json.dumps(farms_data)}

قواعد الرد:
1. ممنوع نهائياً كتابة أي كود HTML أو CSS في ردك (لا تكتب <div... ولا غيره).
2. ابدأ بردك بجملة ترحيبية قصيرة بلهجة أردنية.
3. ضع اقتراحات المزارع حصراً داخل وسم [DATA]...[/DATA] بصيغة JSON فقط.
4. شكل الـ JSON المطلوب:
{{
  "recommendations": [
    {{"name": "اسم المزرعة", "price": 0, "features": "ميزة 1، ميزة 2", "reason": "لماذا اخترتها؟"}}
  ]
}}
5. إذا سألك عن شيء غير المزارع، اعتذر بلطف.
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("event-jo.com - بوابتك لأجمل مزارع المملكة")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("كيف بقدر أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # تجهيز المحادثة
            history = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages[-5:]:
                # حذف أي HTML سابق قبل إرساله للموديل عشان ما يقلده
                clean_msg = re.sub(r'<.*?>', '', msg["content"], flags=re.DOTALL)
                history.append({"role": msg["role"], "content": clean_text if 'clean_text' in locals() else clean_msg})

            chat_completion = client.chat.completions.create(
                messages=history,
                model="llama-3.3-70b-versatile",
                temperature=0.4,
            )
            
            full_res = chat_completion.choices[0].message.content
            
            # 1. استخراج النص الترحيبي (قبل الداتا)
            display_text = full_res.split("[DATA]")[0].strip()
            # التأكد من تنظيف النص من أي JSON قد يهرب خارج الوسوم
            display_text = re.sub(r'\{.*\}', '', display_text, flags=re.DOTALL).strip()

            # 2. استخراج الـ JSON وتحويله لكروت
            cards_html = ""
            json_match = re.search(r"\[DATA\](.*?)\[/DATA\]", full_res, re.DOTALL) or re.search(r"(\{.*\})", full_res, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1 if "[DATA]" in full_res else 0).strip())
                    for rec in data.get("recommendations", []):
                        cards_html += f"""
                        <div class="farm-card">
                            <div class="farm-name">🏠 {rec['name']}</div>
                            <div class="farm-info">💰 <b>السعر:</b> {rec.get('price')} دينار</div>
                            <div class="farm-info">🌟 <b>المميزات:</b> {rec.get('features')}</div>
                            <div class="farm-info">📝 <b>ليش بنصحك فيها:</b> {rec.get('reason')}</div>
                        </div>
                        """
                except:
                    pass

            final_output = display_text + cards_html
            st.markdown(final_output, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
