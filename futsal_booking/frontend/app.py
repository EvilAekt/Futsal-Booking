import streamlit as st
import requests
from datetime import datetime, timedelta
import uuid
import streamlit.components.v1 as components
import pandas as pd


booked_data = {
    "2025-07-18": ["08.00", "10.00", "16.00"],
    "2025-07-19": ["09.00", "14.00", "18.00"],
    "2025-07-20": ["11.00", "13.00", "19.00"],
}

# --- Konfigurasi Halaman & API ---
st.set_page_config(layout="wide", page_title="Futsal Booking", page_icon="⚽")
API_URL = "http://127.0.0.1:8000"

# --- Styling (CSS Injection) ---
def load_css():
    st.markdown("""
    <style>
        :root {
            --primary-color: #DC143C;
            --secondary-color: #1A1A1A;
            --accent-color: #FFFFFF;
            --text-color: #EAEAEA;
            --dark-gray: #333333;
            --card-bg: linear-gradient(145deg, #1f1f1f, #171717);
            --card-border: #444444;
            --glow-color: rgba(220, 20, 60, 0.5);
        }
        body, .stApp {
            background-color: var(--secondary-color);
        }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: var(--text-color) !important;
        }
        .court-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .court-card:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: var(--primary-color);
            box-shadow: 0 8px 30px var(--glow-color);
        }
        .court-card img {
            border-radius: 8px;
            height: 200px;
            object-fit: cover;
            width: 100%;
        }
        .stButton>button {
            border: 2px solid var(--primary-color);
            border-radius: 8px;
            color: var(--accent-color);
            background-color: transparent;
            padding: 10px 24px;
            font-weight: bold;
            width: 150px;
            height: 48px;
            font-size: 16px;
            padding: 8px 12px;
        }
        .stButton>button:hover {
            background-color: var(--primary-color);
            box-shadow: 0 0 15px var(--glow-color);
        }
        .hero {
            padding: 4rem 1rem;
            background: linear-gradient(to bottom, rgba(0,0,0,0.6), var(--secondary-color)), url('https://i.imgur.com/8j6gPg5.jpeg');
            background-size: cover;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .hero h1 {
            font-size: 3.5rem;
            font-weight: 900;
        }
        .hero .highlight {
            color: var(--primary-color) !important;
        }
        .booking-form {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 2rem;
        }
        .success-box {
            border: 1px solid #28a745;
            background-color: rgba(40, 167, 69, 0.1);
            padding: 2rem;
            border-radius: 12px;
        }
        .success-box .booking-id {
            font-family: monospace;
            background: var(--dark-gray);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 1.1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def get_courts_data():
    try:
        response = requests.get(f"{API_URL}/courts/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke server: {e}")
        return []

def get_availability(court_id, date):
    try:
        response = requests.get(f"{API_URL}/courts/{court_id}/availability?date={date}")
        response.raise_for_status()
        return response.json().get("available_slots", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal mengambil jadwal: {e}")
        return []

def book_court(payload):
    try:
        response = requests.post(f"{API_URL}/bookings/", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            st.error("Jadwal yang dipilih sudah tidak tersedia.")
        else:
            st.error(f"Gagal booking: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal terhubung ke server: {e}")
        return None

# --- Session State Init ---
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_court' not in st.session_state:
    st.session_state.selected_court = None
if 'booking_result' not in st.session_state:
    st.session_state.booking_result = None

def navigate_to(page, court=None):
    st.session_state.page = page
    st.session_state.selected_court = court
    st.rerun()

# --- Pages ---
def main_page():
    st.markdown("""
    <div class="hero">
        <h1>FUTSAL <span class="highlight">BOOK</span>, BOOK<span class="highlight">ING</span></h1>
        <p>Temukan dan booking lapangan futsal terbaik dengan sistem yang mudah dan cepat</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    courts = get_courts_data()
    if not courts:
        st.warning("Tidak ada lapangan tersedia.")
        return

    _, _, filter_col = st.columns([2, 2, 1])
    filter_type = filter_col.selectbox("Filter Tipe", ["Semua", "Indoor", "Outdoor", "Premium"], label_visibility="collapsed")

    filtered = [c for c in courts if c['type'] == filter_type] if filter_type != "Semua" else courts
    cols = st.columns(3)
    for i, court in enumerate(filtered):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div class="court-card">
                    <img src="{court['image_url']}" alt="court image" />
                    <h3>{court['name']}</h3>
                    <p><strong>Tipe:</strong> {court['type']} | <strong>Harga:</strong> Rp {court['price']:,.0f}/jam</p>
                    <p><strong>Fasilitas:</strong> {court['facilities']}</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="book-now">', unsafe_allow_html=True)
                if st.button("Book Now", key=f"book_{court['id']}"):
                    navigate_to('booking', court)
                st.markdown('</div>', unsafe_allow_html=True)

def booking_page():
    court = st.session_state.selected_court
    if not court:
        st.error("Lapangan tidak ditemukan.")
        if st.button("Kembali"):
            navigate_to('main')
        return

    if st.button("← Kembali"):
        navigate_to('main')

    st.markdown('<div class="booking-form">', unsafe_allow_html=True)
    st.title(f"Booking: {court['name']}")
    st.image(court['image_url'])
    st.markdown(f"### Harga: Rp {court['price']:,.0f}/jam")

    with st.form("booking_form"):
        selected_date = st.date_input("Tanggal", min_value=datetime.today(), max_value=datetime.today() + timedelta(days=30))
        duration = st.selectbox("Durasi (jam)", [1, 2, 3, 4])
        available_slots = get_availability(court['id'], selected_date.strftime("%Y-%m-%d"))
        start_time = st.radio("Jam Mulai", available_slots, horizontal=True) if available_slots else None

        customer_name = st.text_input("Nama Lengkap")
        customer_phone = st.text_input("Nomor HP")
        customer_email = st.text_input("Email")

        total_price = court['price'] * duration
        st.markdown(f"**Total Harga**: Rp {total_price:,.0f}")

        if st.form_submit_button("Konfirmasi & Booking"):
            if not all([customer_name, customer_phone, customer_email, start_time]):
                st.error("Lengkapi semua data terlebih dahulu.")
            else:
                payload = {
                    "court_id": court['id'],
                    "customer_name": customer_name,
                    "customer_phone": customer_phone,
                    "customer_email": customer_email,
                    "booking_date": selected_date.strftime("%Y-%m-%d"),
                    "start_time": start_time,
                    "duration": duration,
                }
                result = book_court(payload)
                if result:
                    st.session_state.booking_result = {**result, 'court_name': court['name']}
                    navigate_to('success')
    st.markdown('</div>', unsafe_allow_html=True)

def success_page():
    result = st.session_state.booking_result
    if not result:
        st.error("Tidak ada data booking.")
        if st.button("Kembali"):
            navigate_to('main')
        return

    st.balloons()
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.title("✅ Booking Berhasil!")
    st.markdown(f"### Booking ID: <span class='booking-id'>{str(uuid.uuid4())[:8].upper()}</span>", unsafe_allow_html=True)

    tanggal = datetime.strptime(result['booking_date'], "%Y-%m-%d").strftime('%A, %d %B %Y')
    st.markdown(f"""
    - **Nama**: {result['customer_name']}
    - **Lapangan**: {result['court_name']}
    - **Tanggal**: {tanggal}
    - **Jam**: {result['start_time']} ({result['duration']} jam)
    - **Total**: Rp {result['total_price']:,.0f}
    - **Status**: <span style='color:green; font-weight:bold;'>{result['status'].upper()}</span>
    """, unsafe_allow_html=True)

    if st.button("Booking Lagi"):
        navigate_to('main')
    st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar Navigasi ---


with st.sidebar:
    st.markdown("<h1 style='margin-bottom: 30px;'> Futsal Booking</h1>", unsafe_allow_html=True)
    
    # Gaya tombol custom via st.button()
    def nav_button(title, key_name, page_value):
        if st.button(title, key=key_name):
            st.session_state.page = page_value

    # Tombol Navigasi
    nav_button(" Home", "nav_home", "main")
    nav_button(" Jadwal", "nav_jadwal", "jadwal")
    nav_button(" Riwayat", "nav_riwayat", "riwayat")
    nav_button(" Hubungi Kami", "nav_contact", "kontak")

# --- Halaman Sidebar ---
def show_today_schedule():
    selected_date = st.date_input("Pilih Tanggal", datetime.today())
    date_key = selected_date.strftime("%Y-%m-%d")
    booked_hours = booked_data.get(date_key, [])
    hours = [f"{h:02d}.00" for h in range(8, 22)]

    # HTML dan CSS Table
    table_html = f"""
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 18px;
        }}
        th, td {{
            padding: 12px;
            text-align: center;
            border: 1px solid #444;
        }}
        th {{
            background-color: #111;
            color: white;
        }}
        .booked {{
            color: #00FFAA;
            font-weight: bold;
        }}
        .available {{
            color: #FF5555;
        }}
    </style>
    <h3>Jadwal Booking: {selected_date.strftime('%A, %d %B %Y')}</h3>
    <table>
        <tr><th>Jam</th><th>Status</th></tr>
    """

    for hour in hours:
        if hour in booked_hours:
            status = '<span class="booked">Booked</span>'
        else:
            status = '<span class="available">Tersedia</span>'
        table_html += f"<tr><td>{hour}</td><td>{status}</td></tr>"

    table_html += "</table>"

    st.markdown(table_html, unsafe_allow_html=True)


def show_booking_history_summary():
    st.subheader("Riwayat Terakhir")
    st.dataframe([
        {"Tanggal": "16 Juli 2025", "Lapangan": "A", "Jam": "09:00", "Status": "Selesai"},
        {"Tanggal": "15 Juli 2025", "Lapangan": "B", "Jam": "11:00", "Status": "Selesai"},
    ], use_container_width=True)

def show_contact_form():
    st.markdown("""
        <style>
            .contact-container {
                background-color: #111;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 0 15px rgba(0,0,0,0.6);
                color: #eee;
                margin-bottom: 30px;
            }
            .contact-header {
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #aaa;
            }
            .contact-subtext {
                font-size: 16px;
                margin-bottom: 25px;
                color: #bbb;
            }
            .stTextInput > div > input, .stTextArea > div > textarea {
                background-color: #222 !important;
                color: #fff !important;
            }
        </style>
        <div class="contact-container">
            <div class="contact-header">Hubungi Kami</div>
            <div class="contact-subtext">Punya pertanyaan atau butuh bantuan? Kirim pesan atau kunjungi lokasi kami di bawah.</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.form("hubungi_form"):
            nama = st.text_input("Nama Lengkap")
            email = st.text_input("Email")
            pesan = st.text_area("Pesan")
            if st.form_submit_button("Kirim"):
                st.success(f"✅ Pesan dari **{nama}** telah dikirim. Terima kasih!")

        st.markdown(" **WhatsApp:** [0812-3456-7890](https://wa.me/6283157672217)")
        st.markdown(" **Alamat:** Jl. Ring Road Utara, Condongcatur, Sleman, Yogyakarta")
        st.markdown(" **Website:** [www.amikom.ac.id](https://amikom.ac.id)")

    with col2:
        lokasi = pd.DataFrame({'lat': [-7.747033], 'lon': [110.355398]})
        st.map(lokasi, zoom=16)

# --- Routing ---
load_css()
if st.session_state.page == 'main':
    main_page()
elif st.session_state.page == 'booking':
    booking_page()
elif st.session_state.page == 'success':
    success_page()
elif st.session_state.page == 'jadwal':
    st.title("Jadwal")
    show_today_schedule()
elif st.session_state.page == 'riwayat':
    st.title("Riwayat Booking")
    show_booking_history_summary()
elif st.session_state.page == 'kontak':
    st.title("Kontak")
    show_contact_form()
