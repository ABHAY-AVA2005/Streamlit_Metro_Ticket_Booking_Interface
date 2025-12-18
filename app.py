# ============================================================
# UNIFIED CITY COMMUTE APPLICATION (METRO + CAB)
# ============================================================
# Features:
# 1. Metro booking with optional Cab integration
# 2. Dynamic Cab Toggle using Session State (Buttons)
# 3. Car Type Selection (Mini, Sedan, SUV) with dynamic pricing
# 4. QR code generation with unified journey details
# 5. Ticket download & Voice announcement
# ============================================================

# ---------------- IMPORTS ----------------
import streamlit as st          # Streamlit UI framework
import qrcode                   # QR code generation
from gtts import gTTS           # Google Text-to-Speech
from io import BytesIO          # In-memory byte streams
import uuid                     # Unique ticket ID generator

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Unified City Commute",
    page_icon="🏙️",
    layout="centered"
)

# ============================================================
# FUNCTION: GENERATE QR CODE
# ============================================================
def generate_qr_code(ticket_text: str) -> BytesIO:
    """
    Generates a QR code image from ticket text.
    Returns the QR code as a BytesIO object (PNG format).
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(ticket_text)
    qr.make(fit=True)

    # Generate the QR image
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save image to BytesIO buffer
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)   # Reset buffer pointer to start

    return qr_buffer

# ============================================================
# FUNCTION: GENERATE VOICE ANNOUNCEMENT
# ============================================================
def generate_voice_audio(message: str) -> BytesIO:
    """
    Converts text to speech using gTTS.
    Returns the audio as a BytesIO object (MP3 format).
    """
    tts = gTTS(text=message, lang="en")
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)   # Reset buffer pointer to start
    return audio_buffer

# ============================================================
# SESSION STATE (MEMORY FOR CAB TOGGLE)
# ============================================================
if "show_cab_details" not in st.session_state:
    st.session_state.show_cab_details = False

# ============================================================
# CONSTANTS & DATA
# ============================================================
METRO_PRICE = 30

# Different rates per person based on Car Type
CAB_RATES = {
    "Mini": 40,
    "Sedan": 60,
    "SUV": 90
}

STATIONS = [
    "Ameerpet", "KPHB", "Kukatpally", 
    "Madhapur", "Hitech City", "Raidurg"
]

LOCATIONS = [
    "Office", "Home", "Shopping Mall", 
    "Hospital", "College", "Hotel"
]

# ============================================================
# USER INTERFACE: TITLE & PASSENGER DETAILS
# ============================================================
st.title("🏙️ UNIFIED CITY COMMUTE SYSTEM")
st.markdown("### Passenger Details")

passenger_name = st.text_input("Passenger Name")

# ============================================================
# SECTION 1: METRO DETAILS
# ============================================================
st.markdown("### 1. Metro Details")

col1, col2 = st.columns(2)
with col1:
    source_station = st.selectbox("Source Station", STATIONS)
with col2:
    destination_station = st.selectbox("Destination Station", STATIONS, index=1)

ticket_count = st.number_input(
    "Number of Passengers",
    min_value=1,
    max_value=10,
    step=1
)

metro_fare = ticket_count * METRO_PRICE
st.info(f"🚇 Metro Fare: ₹{metro_fare}")

# ============================================================
# SECTION 2: CAB REQUIREMENT
# ============================================================
st.markdown("### 2. Cab Requirement")
st.write("Do you need a cab for the last mile?")

# Buttons for Yes/No
if st.button("YES - Add Cab"):
    st.session_state.show_cab_details = True

if st.button("NO - Metro Only"):
    st.session_state.show_cab_details = False

# Initialize Cab Variables
cab_pickup = "N/A"
cab_drop = "N/A"
cab_fare = 0
selected_car = "None"

# Conditional Cab Input
if st.session_state.show_cab_details:
    st.markdown("#### 🚖 Cab Details")
    
    # Pickup is auto-set to Metro Destination
    cab_pickup = destination_station
    st.text_input("Pickup Location", value=cab_pickup, disabled=True)
    
    # Drop Location
    cab_drop = st.selectbox("Drop Location", LOCATIONS)

    # Car Type Selection
    selected_car = st.selectbox("Select Car Type", list(CAB_RATES.keys()))
    
    # Calculate Cab Fare dynamically based on selection
    rate_per_person = CAB_RATES[selected_car]
    cab_fare = ticket_count * rate_per_person
    
    st.info(f"🚖 Cab Fare ({selected_car}): ₹{cab_fare}")
else:
    st.caption("Status: Cab booking is currently disabled.")

# ============================================================
# FARE CALCULATION & TOTALS
# ============================================================
st.markdown("---")
grand_total = metro_fare + cab_fare
st.markdown(f"### 💰 Grand Total: ₹{grand_total}")

# Generate a short unique ticket ID
ticket_id = str(uuid.uuid4())[:8].upper()

# Determine Button Text
btn_text = "🎫 Book Metro & Cab" if st.session_state.show_cab_details else "🎫 Book Metro Only"

# ============================================================
# BOOK TICKET ACTION
# ============================================================
if st.button(btn_text, type="primary"):

    # -------- VALIDATION ----------
    if passenger_name.strip() == "":
        st.error("Passenger name is required.")
    elif source_station == destination_station:
        st.error("Source and destination stations must be different.")
    else:
        # -------- TICKET TEXT CONSTRUCTION ----------
        if st.session_state.show_cab_details:
            # UNIFIED TICKET
            ticket_text = f"""
UNIFIED JOURNEY TICKET
-------------------------
Ticket ID : {ticket_id}
Passenger : {passenger_name}
-------------------------
[METRO]
From      : {source_station}
To        : {destination_station}
Amount    : ₹{metro_fare}
-------------------------
[CAB]
Car Type  : {selected_car}
Pickup    : {cab_pickup}
Drop      : {cab_drop}
Amount    : ₹{cab_fare}
-------------------------
GRAND TOTAL : ₹{grand_total}
-------------------------
            """
            voice_msg = (
                f"Hello {passenger_name}. "
                f"Your metro from {source_station} to {destination_station}, "
                f"and {selected_car} cab to {cab_drop} is booked. "
                f"Total amount is rupees {grand_total}."
            )
        else:
            # METRO ONLY TICKET
            ticket_text = f"""
METRO TICKET
-------------------------
Ticket ID : {ticket_id}
Passenger : {passenger_name}
From      : {source_station}
To        : {destination_station}
Tickets   : {ticket_count}
Amount    : ₹{metro_fare}
-------------------------
            """
            voice_msg = (
                f"Hello {passenger_name}. "
                f"Your metro ticket from {source_station} to {destination_station} "
                f"is booked successfully. "
                f"Total amount is rupees {metro_fare}."
            )

        # -------- QR CODE GENERATION ----------
        qr_bytes = generate_qr_code(ticket_text)

        # -------- DISPLAY RESULTS ----------
        st.success("✅ Booking Confirmed Successfully")

        st.markdown("### 🧾 Ticket Details")
        st.text(ticket_text)

        st.markdown("### 📱 QR Code")
        st.image(qr_bytes, width=200)

        # -------- DOWNLOAD OPTIONS ----------
        st.markdown("### ⬇ Download Ticket")

        # Download QR code as PNG
        st.download_button(
            label="⬇ Download QR Code (PNG)",
            data=qr_bytes,
            file_name=f"Journey_{ticket_id}.png",
            mime="image/png"
        )

        # Download ticket details as TXT
        st.download_button(
            label="⬇ Download Ticket Details (TXT)",
            data=ticket_text,
            file_name=f"Journey_{ticket_id}.txt",
            mime="text/plain"
        )

        # -------- VOICE ANNOUNCEMENT ----------
        audio_bytes = generate_voice_audio(voice_msg)

        st.markdown("### 🔊 Voice Announcement")
        st.audio(audio_bytes, format="audio/mp3")
