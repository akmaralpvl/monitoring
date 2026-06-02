import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы
st.set_page_config(page_title="Мониторинг успеваемости", layout="wide")

# --- СТИЛИЗАЦИЯ (ТЕПЛАЯ ТЕМА) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdf6e3; color: #5d4037; }
    .stSidebar { background-color: #f5e6ca; }
    h1, h2, h3 { color: #3e2723 !important; }
    .stButton>button { border-radius: 10px; background-color: #d7ccc8; }
    </style>
    """, unsafe_allow_html=True)

# --- ЯЗЫКОВАЯ ПАНЕЛЬ ---
lang = st.sidebar.radio("🌐 Тіл / Язык:", ["Русский", "Қазақша"])
texts = {
    "Русский": {
        "welcome": "Добро пожаловать в систему мониторинга!",
        "settings": "Настройка данных",
        "file1": "Загрузите 1-й файл (База)",
        "file2": "Загрузите 2-й файл (Сравнение)",
        "chart_title": "📊 Сравнительный анализ среднего балла",
        "leaders": "🚀 Лидеры роста",
        "attention": "⚠️ Требуют внимания",
        "forecast": "🔮 Прогноз и работа с группой риска",
        "forecast_text": "Ученики с отрицательной динамикой рискуют получить снижение оценки.",
        "subj_analysis": "📈 Анализ по предметам",
        "select_student": "👤 Выберите ученика:",
        "uploader_help": "Перетащите файл (.xlsx) сюда",
        "arrived": "➕ Прибывшие",
        "left": "➖ Выбывшие",
        "support_list": "📋 Список учеников, нуждающихся в поддержке:"
    },
    "Қазақша": {
        "welcome": "Мониторинг жүйесіне қош келдіңіз!",
        "settings": "Деректерді баптау",
        "file1": "1-ші файлды жүктеңіз (База)",
        "file2": "2-ші файлды жүктеңіз (Салыстыру)",
        "chart_title": "📊 Орташа баллдың салыстырмалы талдауы",
        "leaders": "🚀 Өсу лидерлері",
        "attention": "⚠️ Назар аударуды қажет етеді",
        "forecast": "🔮 Болжам және тәуекел тобымен жұмыс",
        "forecast_text": "Динамикасы теріс оқушылар шара қолданбаса, бағалары төмендеуі мүмкін.",
        "subj_analysis": "📈 Пәндер бойынша талдау",
        "select_student": "👤 Оқушыны таңдаңыз:",
        "uploader_help": "Файлды (.xlsx) осы жерге апарып тастаңыз",
        "arrived": "➕ Келгендер",
        "left": "➖ Кеткендер",
        "support_list": "📋 Қолдауды қажет ететін оқушылар тізімі:"
    }
}
t = texts[lang]

# --- ИНТЕРФЕЙС ---
st.title("✨ " + t["welcome"])

st.sidebar.header("⚙️ " + t["settings"])
file_1 = st.sidebar.file_uploader("📥 " + t["file1"], type=["xlsx", "xls"], key="f1", help=t["uploader_help"])
file_2 = st.sidebar.file_uploader("📤 " + t["file2"], type=["xlsx", "xls"], key="f2", help=t["uploader_help"])

# ПРИВЕТСТВИЕ
if file_1 is None or file_2 is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.freepik.com/free-vector/hand-drawn-flat-design-mba-illustration_23-2149331623.jpg", width=300)

def load_data(file):
    df_raw = pd.read_excel(file, header=None)
    header_idx = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains('Фамилия|Аты|Имя', case=False).any(), axis=1)].index[0]
    df = pd.read_excel(file, header=header_idx)
    df.columns = df.columns.astype(str).str.strip()
    name_col = [c for c in df.columns if 'Фамилия' in c or 'Имя' in c or 'Аты' in c][0]
    df = df.groupby(name_col).mean(numeric_only=True)
    return df

# --- ЛОГИКА ---
if file_1 is not None and file_2 is not None:
    try:
        df1 = load_data(file_1)
        df2 = load_data(file_2)
        
        common_students = df1.index.intersection(df2.index)
        arrived = df2.index.difference(df1.index)
        left = df1.index.difference(df2.index)
        
        col_status1, col_status2 = st.columns(2)
        if len(arrived) > 0: col_status1.success(f"{t['arrived']}: {', '.join(arrived)}")
        if len(left) > 0: col_status2.warning(f"{t['left']}: {', '.join(left)}")
        
        df1_common = df1.loc[common_students]
        df2_common = df2.loc[common_students]
        score_col = [c for c in df1.columns if 'Ср. балл' in c or 'Средний' in c or 'Балл' in c][0]
        
        comp = pd.DataFrame({'Старт': df1_common[score_col], 'Итог': df2_common[score_col]})
        comp['Разница'] = (comp['Итог'] - comp['Старт']).round(2)
        
        st.subheader(t["chart_title"])
        fig = px.bar(comp.reset_index(), x=comp.index, y='Разница', color='Разница', color_continuous_scale='RdYlGn', text_auto='.2f')
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t["leaders"])
            st.dataframe(comp[comp['Разница'] > 0].sort_values('Разница', ascending=False).style.format("{:+.2f}"), use_container_width=True)
        with col2:
            st.subheader(t["attention"])
            st.dataframe(comp[comp['Разница'] < 0].sort_values('Разница').style.format("{:+.2f}"), use_container_width=True)
            
        st.divider()
        st.subheader(t["subj_analysis"])
        diff_df = (df2_common - df1_common).round(2)
        valid_students = diff_df[diff_df.count(axis=1) > 1].index
        selected_student = st.selectbox(t["select_student"], valid_students)
        
        student_data = diff_df.loc[selected_student]
        fig_subj = px.bar(x=student_data.index, y=student_data.values, color=student_data.values, color_continuous_scale='RdYlGn', text_auto='.2f')
        st.plotly_chart(fig_subj, use_container_width=True)
        
        st.divider()
        st.subheader(t["forecast"])
        negative_dynamics = comp[comp['Разница'] < 0].sort_values('Разница')
        
        if not negative_dynamics.empty:
            st.warning(t["forecast_text"])
            st.write(t["support_list"]) # Теперь берем перевод из словаря
            for student, row in negative_dynamics.iterrows():
                st.write(f"- **{student}**: {row['Разница']:+g} балла")
        else:
            st.success("✅ Отличная работа! У всех учеников положительная или стабильная динамика.")

    except Exception as e:
        st.error(f"Ошибка обработки файлов: {e}")
