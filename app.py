# ============================================================
# METRO TICKET BOOKING APPLICATION (STREAMLIT-ONLY)
# ============================================================
# Features:
# 1. Passenger ticket booking interface
# 2. QR code generation with full ticket details
# 3. Ticket download (QR as PNG + Ticket as TXT)
# 4. Voice announcement using gTTS (played via st.audio)
# ============================================================

# ---------------- IMPORTS ----------------
import streamlit as st          # Streamlit UI framework
import qrcode                   # QR code generation
from gtts import gTTS           # Google Text-to-Speech
from io import BytesIO          # In-memory byte streams
import uuid                     # Unique ticket ID generator

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Metro Ticket Booking",
    page_icon="🚇",
    layout="centered"
)

# ============================================================
# FUNCTION: GENERATE QR CODE
# ============================================================
def generate_qr_code(ticket_text: str) -> BytesIO:
    """
    Generates a QR code image from ticket text.
    Returns the QR code as a BytesIO object (PNG format)
    suitable for display or download in Streamlit.
    """
    qr = qrcode.QRCode(
        version=1,        # QR code size (1 is smallest)
        box_size=8,       # Size of each box in pixels
        border=4          # Thickness of border
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
    Returns the audio as a BytesIO object (MP3 format)
    which can be played in Streamlit using st.audio().
    """
    tts = gTTS(text=message, lang="en")
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)   # Reset buffer pointer to start
    return audio_buffer

# ============================================================
# USER INTERFACE: TITLE & PASSENGER DETAILS
# ============================================================
st.title("🚇 METRO TICKET BOOKING SYSTEM")
st.markdown("### Passenger Details")

# List of metro stations
stations = [
    "Ameerpet",
    "KPHB",
    "Kukatpally",
    "Madhapur",
    "Nizampet"
]

# Input: Passenger name
passenger_name = st.text_input("Passenger Name")

# Input: Source and destination stations
source_station = st.selectbox("Source Station", stations)
destination_station = st.selectbox("Destination Station", stations)

# Input: Number of tickets (1-5)
ticket_count = st.number_input(
    "Number of Tickets",
    min_value=1,
    max_value=5,
    step=1
)

# ============================================================
# FARE CALCULATION
# ============================================================
PRICE_PER_TICKET = 30                   # Fixed ticket price
total_fare = ticket_count * PRICE_PER_TICKET

st.info(f"💰 Total Fare: ₹{total_fare}")

# Generate a short unique ticket ID
ticket_id = str(uuid.uuid4())[:8]

# ============================================================
# BOOK TICKET BUTTON
# ============================================================
if st.button("🎫 Book Ticket"):

    # -------- VALIDATION ----------
    if passenger_name.strip() == "":
        st.error("Passenger name is required.")
    elif source_station == destination_station:
        st.error("Source and destination stations must be different.")
    else:
        # -------- TICKET TEXT ----------
        ticket_text = f"""
METRO TICKET
-------------------------
Ticket ID : {ticket_id}
Passenger : {passenger_name}
From      : {source_station}
To        : {destination_station}
Tickets   : {ticket_count}
Amount    : ₹{total_fare}
-------------------------
        """

        # -------- QR CODE GENERATION ----------
        qr_bytes = generate_qr_code(ticket_text)

        # -------- DISPLAY TICKET ----------
        st.success("✅ Ticket Booked Successfully")

        st.markdown("### 🧾 Ticket Details")
        st.text(ticket_text)

        st.markdown("### 📱 QR Code")
        st.image(qr_bytes, width=250)

        # -------- DOWNLOAD OPTIONS ----------
        st.markdown("### ⬇ Download Ticket")

        # Download QR code as PNG
        st.download_button(
            label="⬇ Download QR Code (PNG)",
            data=qr_bytes,
            file_name=f"Metro_Ticket_{ticket_id}.png",
            mime="image/png"
        )

        # Download ticket details as TXT
        st.download_button(
            label="⬇ Download Ticket Details (TXT)",
            data=ticket_text,
            file_name=f"Metro_Ticket_{ticket_id}.txt",
            mime="text/plain"
        )

        # -------- VOICE ANNOUNCEMENT ----------
        voice_message = (
            f"Hello {passenger_name}. "
            f"Your metro ticket from {source_station} to {destination_station} "
            f"for {ticket_count} tickets has been booked successfully. "
            f"Total amount is rupees {total_fare}. "
            f"Thank you for using Metro Service."
        )

        audio_bytes = generate_voice_audio(voice_message)

        st.markdown("### 🔊 Voice Announcement")
        st.audio(audio_bytes, format="audio/mp3")
