import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import PyPDF2

st.set_page_config(page_title="DeThi7991 - Tú", layout="wide")
st.title("Trang Cá Nhân của Tú - Tạo Ma Trận & Đề Thi THCS")
st.subheader("Theo Công văn 7991/BGDĐT-GDTrH ngày 17/12/2024 & Phụ lục Bộ GDĐT")

uploaded_doc = st.file_uploader("Tải file Phân phối chương trình (Word/PDF)", type=["docx", "pdf"])
uploaded_content = st.file_uploader("Tải nội dung bài học (PDF, nhiều file OK)", type=["pdf"], accept_multiple_files=True)

api_key = st.text_input("Nhập Gemini API Key", type="password")

level = st.selectbox("Lớp", ["Lớp 6", "Lớp 7", "Lớp 8", "Lớp 9"])
ky = st.selectbox("Kỳ kiểm tra", ["Giữa Kỳ 1", "Cuối Kỳ 1", "Giữa Kỳ 2", "Cuối Kỳ 2"])

col1, col2 = st.columns(2)
with col1:
    num_tn = st.number_input("Số câu Trắc nghiệm", min_value=10, value=20)
with col2:
    num_tl = st.number_input("Số câu Tự luận", min_value=3, value=5)

if st.button("Tạo Ma Trận + Đặc Tả + Đề Thi theo CV 7991"):
    if not api_key:
        st.error("Nhập API Key Gemini trước nhé!")
    elif not uploaded_doc:
        st.error("Tải file phân phối chương trình!")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')

            def read_file(file):
                text = ""
                if file.type == "application/pdf":
                    pdf = PyPDF2.PdfReader(BytesIO(file.read()))
                    for page in pdf.pages:
                        text += (page.extract_text() or "") + "\n"
                else:
                    doc = Document(BytesIO(file.read()))
                    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                return text.strip()

            doc_text = read_file(uploaded_doc)
            content_text = ""
            for f in uploaded_content:
                content_text += read_file(f) + "\n\n"

            prompt = f"""
Tạo theo đúng mẫu Công văn 7991/BGDĐT-GDTrH (ma trận bảng với cột TT, Chủ đề, Nội dung, mức Biết/Hiểu/Vận dụng riêng cho Nhiều lựa chọn, "Đúng-Sai", Trả lời ngắn, Tự luận; bản đặc tả có cột Yêu cầu cần đạt; tỉ lệ khoảng 30% Biết, 20% Hiểu, 20-30% Vận dụng).
Môn Địa lý/Lịch sử lớp {level} - kỳ {ky}.
Phân phối: {doc_text[:12000]}
Nội dung: {content_text[:18000] or "Sử dụng nội dung sách Kết nối tri thức với cuộc sống"}
Số câu: {num_tn} TN + {num_tl} TL.
Xuất đúng 3 phần: 1. MA TRẬN ĐỀ KIỂM TRA ĐỊNH KÌ (bảng giống phụ lục 1), 2. BẢN ĐẶC TẢ (bảng giống phụ lục 2), 3. ĐỀ THI CHÍNH THỨC.
"""

            with st.spinner("Đang tạo theo mẫu Bộ GDĐT... chờ 20-60 giây"):
                response = model.generate_content(prompt)
                result = response.text

            st.success("Hoàn thành!")
            st.markdown(result)

            doc_out = Document()
            doc_out.add_heading(f"Ma trận & Đề thi lớp {level} - {ky} (CV 7991)", 0)
            doc_out.add_paragraph(result)
            bio = BytesIO()
            doc_out.save(bio)
            bio.seek(0)

            st.download_button("Tải file Word chuẩn", bio, f"CV7991_{level}_{ky}.docx")

        except Exception as e:
            st.error(f"Lỗi: {e}. Kiểm tra API Key hoặc file.")
