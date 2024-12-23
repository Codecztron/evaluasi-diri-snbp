import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser
import re

# Fungsi untuk menghitung rata-rata nilai rapor
def calculate_average_grade(grades):
    """Menghitung rata-rata nilai rapor."""
    filled_grades = [grade for grade in grades if grade > 0]
    return sum(filled_grades) / len(filled_grades) if len(filled_grades) > 0 else 0

# Fungsi untuk memvisualisasikan grafik nilai rapor
def visualize_grades(grades):
    """Memvisualisasikan grafik nilai rapor."""
    semesters = range(1, len(grades) + 1)
    plt.figure()
    plt.plot(semesters, grades, marker='o')
    plt.xlabel("Semester")
    plt.ylabel("Nilai Rata-rata")
    plt.title("Grafik Nilai Rapor")
    plt.xticks(semesters)
    st.pyplot(plt)

# Fungsi untuk memprediksi peluang berdasarkan data CSV atau input manual
def predict_chance(df, university, major, average_grade, snbp_ref_manual=None):
    """
    Memprediksi peluang masuk berdasarkan data CSV atau input manual.
    """
    if df is not None:
        filtered_df = df[
            (df["UNIV"] == university) & (df["JURUSAN"] == major)
        ]

        if filtered_df.empty:
            return None, None, None, None, None, None, None, None, None, None, None

        # Handle potential missing or non-numeric values gracefully
        total_applicants_snbp = safe_convert(filtered_df["PENDAFTAR SNBP"].iloc[0], int, 0)
        accepted_snbp = safe_convert(filtered_df["DITERIMA SNBP"].iloc[0], int, 0)
        total_applicants_snbt = safe_convert(filtered_df["PENDAFTAR SNBT"].iloc[0], int, 0)
        accepted_snbt = safe_convert(filtered_df["DITERIMA SNBT"].iloc[0], int, 0)
        snbp_ref = safe_convert(filtered_df["SNBP"].iloc[0], float, 0.0)
        snbt_ref = safe_convert(filtered_df["SNBT"].iloc[0], float, 0.0)

        # Ekstrak nilai keketatan dan konversi menjadi float
        keketatan_snbp_str = filtered_df["KEKETATAN SNBP"].iloc[0] if "KEKETATAN SNBP" in filtered_df.columns else "0:0"
        keketatan_snbt_str = filtered_df["KEKETATAN SNBT"].iloc[0] if "KEKETATAN SNBT" in filtered_df.columns else "0:0"
        
        def ratio_to_float(ratio_str):
            match = re.match(r"(\d+):(\d+)", ratio_str)
            if match:
                try:
                    return float(match.group(1)) / float(match.group(2))
                except ZeroDivisionError:
                    return 0.0
            else:
                return 0.0

        keketatan_snbp = ratio_to_float(keketatan_snbp_str)
        keketatan_snbt = ratio_to_float(keketatan_snbt_str)

        chance_snbp = (
            (accepted_snbp / total_applicants_snbp) * 100 if total_applicants_snbp > 0 else 0
        )
        chance_snbt = (
            (accepted_snbt / total_applicants_snbt) * 100 if total_applicants_snbt > 0 else 0
        )

        required_increase = None
        if average_grade < snbp_ref:
            required_increase = snbp_ref + 2 - average_grade

        return chance_snbp, chance_snbt, required_increase, snbp_ref, snbt_ref, total_applicants_snbp, accepted_snbp, total_applicants_snbt, accepted_snbt, keketatan_snbp, keketatan_snbt

    else:
        required_increase = None
        if average_grade < snbp_ref_manual:
            required_increase = snbp_ref_manual + 2 - average_grade

        return None, None, required_increase, snbp_ref_manual, None, None, None, None, None, None, None

# Helper function for safe type conversion
def safe_convert(value, target_type, default_value):
    """Converts a value to a target type, returning a default value on failure."""
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default_value

# --- Streamlit App --- 
st.title("Aplikasi Prediksi Peluang SNBP dan SNBT")
st.write("by Codecztron (Andri)")
st.markdown("Jika aplikasi ini bermanfaat, Anda dapat memberikan dukungan dengan [Donasi via Saweria](https://saweria.co/Codecztron) :heart:")


# Sidebar untuk input data
st.sidebar.header("Input Data")

st.sidebar.subheader("Data Rapor")
num_semesters = 5
grades = []
for i in range(num_semesters):
    grade = st.sidebar.number_input(f"Nilai Rata-rata Semester {i+1}", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    grades.append(grade)

st.sidebar.subheader("Pilihan Sumber Data")
data_source = st.sidebar.radio("Pilih sumber data:", ("Database", "Input Manual"))

if data_source == "Database":
    st.sidebar.subheader("Pilihan Universitas dan Jurusan")
    try:
        # Coba baca data.csv
        df = pd.read_csv("data/data.csv", sep=";", thousands=".", decimal=",")

        # Handle potential missing columns
        required_columns = ["UNIV", "JURUSAN", "PENDAFTAR SNBP", "DITERIMA SNBP", "PENDAFTAR SNBT", "DITERIMA SNBT", "SNBP", "SNBT"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"File 'data.csv' tidak memiliki kolom yang diperlukan: {', '.join(missing_columns)}. Pastikan format file CSV sudah benar atau gunakan opsi 'Input Manual'.")
            st.stop()

        universities = df["UNIV"].unique()
        university = st.sidebar.selectbox("Pilih Universitas", universities)

        majors = df[df["UNIV"] == university]["JURUSAN"].unique()
        major = st.sidebar.selectbox("Pilih Jurusan", majors)

    except FileNotFoundError:
        st.error("File database 'data.csv' tidak ditemukan. Pastikan file tersebut ada di direktori yang sama dengan aplikasi atau unggah ke repository GitHub Anda dan pilih 'Input Manual' untuk memasukkan data secara manual.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file 'data.csv': {e}. Pastikan format file CSV sudah benar.")
        st.stop()

else:  # Input Manual
    st.sidebar.subheader("Input Manual Nilai Referensi SNBP")
    university = st.sidebar.text_input("Masukkan Nama Universitas (Opsional)")
    major = st.sidebar.text_input("Masukkan Nama Jurusan (Opsional)")
    snbp_ref_manual = st.sidebar.number_input("Masukkan Nilai Referensi SNBP PTN tujuan / Target Nilai", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    df = None

# --- Main Content ---

average_grade = calculate_average_grade(grades)
st.write(f"**Rata-rata Nilai Rapor:** {average_grade:.2f}")

st.subheader("Grafik Nilai Rapor")
visualize_grades(grades)

if data_source == "Database":
    if 'df' in locals() and 'university' in locals() and 'major' in locals():
        chance_snbp, chance_snbt, required_increase, snbp_ref, snbt_ref, total_applicants_snbp, accepted_snbp, total_applicants_snbt, accepted_snbt, keketatan_snbp, keketatan_snbt = predict_chance(
            df, university, major, average_grade
        )

        st.subheader("Prediksi Peluang")
        st.write("Source www.mykampus.id")
        st.write("Data berikut diambil pada tahun 2022-2024, dan pasti setiap tahun pasti mengalami kenaikan.")
        st.write("Semoga bisa menjadi patokan nilai untuk kedepannya.")


        if snbp_ref is not None:
            st.write(f"**Nilai** SNBP: **{snbp_ref:.2f}**")
            st.write(f"**Nilai** aman SNBP untuk jurusan ini: **{snbp_ref + 2:.2f}**")
        if snbt_ref is not None:
            st.write(f"**Nilai** SNBT: **{snbt_ref:.2f}**")

        # Menampilkan tabel
        if chance_snbp is not None and chance_snbt is not None:
            data = {
                "Jalur": ["SNBP", "SNBT"],
                "Peluang": [f"{chance_snbp:.2f}%", f"{chance_snbt:.2f}%"],
                "Pendaftar": [total_applicants_snbp, total_applicants_snbt],
                "Diterima": [accepted_snbp, accepted_snbt],
                "Keketatan": [keketatan_snbp, keketatan_snbt],
            }
            df_table = pd.DataFrame(data)
            st.dataframe(df_table.set_index('Jalur'))

            target_average = snbp_ref + 2

            if required_increase is not None and average_grade < snbp_ref:
                st.subheader("**Saran:**")
                current_semester = len([g for g in grades if g > 0])
                if current_semester < 5:
                    st.write(f"Kamu saat ini berada di semester {current_semester}")
                    remaining_semesters = 5 - current_semester
                    k = 0.5
                    total_weight = sum(k**i for i in range(remaining_semesters))
                    increase_per_semester = []
                    target_grades = []
                    current_average = average_grade

                    for i in range(remaining_semesters):
                        increase = (required_increase * (k**i) / total_weight)
                        target_grade = min(current_average + increase, 100)
                        increase_per_semester.append(increase)
                        target_grades.append(target_grade)
                        current_average = target_grade

                    for i in range(remaining_semesters):
                        st.write(f"- Semester {current_semester + 1 + i}: Dapatkan nilai minimal **{target_grades[i]:.2f}**")

                st.write(f"Target nilai aman untuk masuk jurusan ini adalah **{target_average:.2f}**")
            elif average_grade >= snbp_ref:
              st.write("**Selamat!** Nilai rata-rata rapormu sudah memenuhi syarat untuk mendaftar di jurusan ini. Pertahankan prestasimu!")
              st.write(f"Target nilai aman untuk masuk jurusan ini adalah **{target_average:.2f}**")
        else:
            st.write("Data universitas atau jurusan tidak ditemukan.")
    else:
        st.write("Silahkan lengkapi data di atas")

elif data_source == "Input Manual":
    chance_snbp, chance_snbt, required_increase, snbp_ref, snbt_ref, total_applicants_snbp, accepted_snbp, total_applicants_snbt, accepted_snbt, keketatan_snbp, keketatan_snbt = predict_chance(
        df, university, major, average_grade, snbp_ref_manual
    )

    st.subheader("Prediksi Peluang (Input Manual)")

    if snbp_ref is not None:
      st.write(f"Nilai Referensi SNBP (Input Manual): **{snbp_ref:.2f}**")
      st.write(f"Nilai aman SNBP untuk jurusan ini: **{snbp_ref + 2:.2f}**")
      target_average = snbp_ref + 2
    else:
      target_average = 0.0
      st.write("Nilai Referensi SNBP (Input Manual): **Tidak diisi**")
      st.write(f"Nilai aman SNBP untuk jurusan ini: **Tidak diisi**")

    if required_increase is not None:
        st.subheader("**Saran:**")
        current_semester = len([g for g in grades if g > 0])

        if current_semester < 5:
            st.write(f"Kamu saat ini berada di semester {current_semester}")
            remaining_semesters = 5 - current_semester
            k = 0.5
            total_weight = sum(k**i for i in range(remaining_semesters))
            increase_per_semester = []
            target_grades = []
            current_average = average_grade

            for i in range(remaining_semesters):
                increase = (required_increase * (k**i) / total_weight)
                target_grade = min(current_average + increase, 100)
                increase_per_semester.append(increase)
                target_grades.append(target_grade)
                current_average = target_grade
            for i in range(remaining_semesters):
                st.write(f"- Semester {current_semester + 1 + i}: Dapatkan nilai minimal **{target_grades[i]:.2f}**")
        st.write(f"Target nilai aman untuk masuk jurusan ini adalah **{target_average:.2f}**")

    elif average_grade >= snbp_ref:
      st.write("**Selamat!** Nilai rata-rata rapormu sudah memenuhi syarat untuk mendaftar di jurusan ini. Pertahankan prestasimu!")
      st.write(f"Target nilai aman untuk masuk jurusan ini adalah **{target_average:.2f}**")
    
else:
    st.write("Silahkan lengkapi data di atas")