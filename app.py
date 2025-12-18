# ============================================================
# UNIFIED CITY COMMUTE APPLICATION
# ============================================================
# Description: 
# A Streamlit app to book Metro tickets with an optional 
# "Last Mile" Cab service. Features dynamic pricing, QR code 
# generation, and downloadable tickets.
# ============================================================

# ---------------- 1. IMPORTS ----------------
import streamlit as st          # Web App Framework
import qrcode                   # QR Code Generator
from io import BytesIO          # Memory handling for images
import uuid                     # Unique ID Generator

# ---------------- 2. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Unified City Commute",
    page_icon="🏙️",
    layout="centered"
)

# ---------------- 3. HELPER FUNCTIONS ----------------

def generate_qr_code(ticket_text: str) -> BytesIO:
    """
    Generates a QR code image from the provided text.
    Returns: An in-memory image buffer (BytesIO).
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(ticket_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer

# ---------------- 4. SESSION STATE ----------------
# Initializes memory to remember if the user clicked "Yes" for a cab
if "show_cab_details" not in st.session_state:
    st.session_state.show_cab_details = False

# ---------------- 5. CONSTANTS & DATA ----------------
METRO_PRICE = 30  # Flat rate per ticket

# Cab rates per passenger
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
# MAIN USER INTERFACE
# ============================================================

def main():
    st.title("🏙️ UNIFIED CITY COMMUTE")
    st.caption("Seamless Metro & Cab Booking System")
    
    # --- Passenger Details ---
    st.markdown("### 👤 Passenger Details")
    passenger_name = st.text_input("Full Name", placeholder="Enter your name")

    st.markdown("---")

    # --- Section 1: Metro Details ---
    st.markdown("### 🚇 1. Metro Details")

    col1, col2 = st.columns(2)
    with col1:
        source_station = st.selectbox("Source Station", STATIONS)
    with col2:
        # Default destination set to 2nd item for convenience
        destination_station = st.selectbox("Destination Station", STATIONS, index=1)

    ticket_count = st.number_input("Number of Passengers", min_value=1, max_value=10, step=1)
    
    metro_fare = ticket_count * METRO_PRICE
    st.info(f"Metro Fare: ₹{metro_fare}")

    st.markdown("---")

    # --- Section 2: Cab Requirement ---
    st.markdown("### 🚖 2. Cab Requirement")
    st.write("Do you need a connecting cab for the last mile?")

    # Layout buttons side-by-side
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("✅ YES - Add Cab"):
            st.session_state.show_cab_details = True
            
    with btn_col2:
        if st.button("❌ NO - Metro Only"):
            st.session_state.show_cab_details = False

    # Initialize variables to avoid errors
    cab_pickup = "N/A"
    cab_drop = "N/A"
    cab_fare = 0
    selected_car = "None"

    # Show Cab Options if 'YES' was clicked
    if st.session_state.show_cab_details:
        st.markdown("#### Cab Details")
        
        # Auto-fill Pickup using Metro Destination
        cab_pickup = destination_station
        st.text_input("Pickup Location (Auto-filled)", value=cab_pickup, disabled=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cab_drop = st.selectbox("Drop Location", LOCATIONS)
        with col_c2:
            selected_car = st.selectbox("Car Type", list(CAB_RATES.keys()))

        # Calculate Cab Fare
        cab_fare = ticket_count * CAB_RATES[selected_car]
        st.success(f"Cab Fare ({selected_car}): ₹{cab_fare}")
    else:
        st.caption("Status: Cab booking is currently disabled.")

    # --- Section 3: Final Totals ---
    st.markdown("---")
    grand_total = metro_fare + cab_fare
    st.markdown(f"### 💰 Grand Total: ₹{grand_total}")

    # --- Booking Button Logic ---
    btn_label = "🎫 Book Metro & Cab" if st.session_state.show_cab_details else "🎫 Book Metro Only"

    if st.button(btn_label, type="primary"):
        handle_booking(
            passenger_name, source_station, destination_station, 
            ticket_count, metro_fare, cab_pickup, cab_drop, 
            cab_fare, grand_total, selected_car
        )

# ============================================================
# BOOKING LOGIC HANDLER
# ============================================================

def handle_booking(name, src, dest, count, m_fare, c_pickup, c_drop, c_fare, total, car_type):
    
    # 1. Validation
    if not name.strip():
        st.error("⚠️ Please enter the passenger name.")
        return
    if src == dest:
        st.error("⚠️ Source and Destination stations cannot be the same.")
        return

    # 2. Generate Unique ID
    ticket_id = str(uuid.uuid4())[:8].upper()

    # 3. Generate Ticket Text
    if st.session_state.show_cab_details:
        ticket_text = (
            f"UNIFIED JOURNEY TICKET\n"
            f"=========================\n"
            f"ID       : {ticket_id}\n"
            f"Passenger: {name}\n"
            f"-------------------------\n"
            f"[METRO]\n"
            f"Route    : {src} -> {dest}\n"
            f"Fare     : ₹{m_fare}\n"
            f"-------------------------\n"
            f"[CAB]\n"
            f"Type     : {car_type}\n"
            f"Route    : {c_pickup} -> {c_drop}\n"
            f"Fare     : ₹{c_fare}\n"
            f"-------------------------\n"
            f"TOTAL    : ₹{total}\n"
            f"========================="
        )
    else:
        ticket_text = (
            f"METRO TICKET\n"
            f"=========================\n"
            f"ID       : {ticket_id}\n"
            f"Passenger: {name}\n"
            f"-------------------------\n"
            f"Route    : {src} -> {dest}\n"
            f"Count    : {count}\n"
            f"Fare     : ₹{m_fare}\n"
            f"-------------------------\n"
            f"TOTAL    : ₹{total}\n"
            f"========================="
        )

    # 4. Generate QR Code
    qr_img = generate_qr
