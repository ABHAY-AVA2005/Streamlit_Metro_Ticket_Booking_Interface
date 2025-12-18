# ============================================================
# UNIFIED CITY COMMUTE APPLICATION
# ============================================================
# Description:
# A Streamlit app for booking Metro tickets with an optional
# "Last Mile" Cab service. It uses a Radio Button toggle to
# manage state without needing st.session_state.
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

# ---------------- 4. CONSTANTS & DATA ----------------
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
    st.title("🏙️ UNIFIED CITY COMMUTE SYSTEM")
    st.markdown("### Passenger Details")

    passenger_name = st.text_input("Passenger Name", placeholder="Enter full name")

    # --- Section 1: Metro Details ---
    st.markdown("### 1. Metro Details")

    col1, col2 = st.columns(2)
    with col1:
        source_station = st.selectbox("Source Station", STATIONS)
    with col2:
        # Default destination set to 2nd item for convenience
        destination_station = st.selectbox("Destination Station", STATIONS, index=1)

    ticket_count = st.number_input("Number of Passengers", min_value=1, value=1)
    
    metro_fare = ticket_count * METRO_PRICE
    st.info(f"🚇 Metro Fare: ₹{metro_fare}")

    # --- Section 2: Cab Requirement ---
    st.markdown("### 2. Cab Requirement")
    st.write("Do you need a cab for the last mile?")

    # Using Radio with horizontal=True ensures the menu stays open
    # without needing session_state complexity.
    cab_choice = st.radio(
        label="Select Option",
        options=["NO - Metro Only", "YES - Add Cab"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Initialize Cab Variables
    need_cab = (cab_choice == "YES - Add Cab")
    cab_pickup = "N/A"
    cab_drop = "N/A"
    cab_fare = 0
    selected_car = "None"

    if need_cab:
        st.markdown("#### 🚖 Cab Details")
        
        # Pickup is auto-set to Metro Destination
        cab_pickup = destination_station
        st.text_input("Pickup Location (Auto-filled)", value=cab_pickup, disabled=True)
        
        cab_drop = st.selectbox("Drop Location", LOCATIONS)
        selected_car = st.selectbox("Select Car Type", list(CAB_RATES.keys()))
        
        cab_fare = ticket_count * CAB_RATES[selected_car]
        st.info(f"🚖 Cab Fare ({selected_car}): ₹{cab_fare}")

    # --- Section 3: Final Totals ---
    st.markdown("---")
    grand_total = metro_fare + cab_fare
    st.markdown(f"### 💰 Grand Total: ₹{grand_total}")

    # --- Booking Logic ---
    ticket_id = str(uuid.uuid4())[:8].upper()
    btn_text = "🎫 Book Metro & Cab" if need_cab else "🎫 Book Metro Only"

    if st.button(btn_text, type="primary"):
        
        # 1. Validation
        if not passenger_name.strip():
            st.error("⚠️ Passenger name is required.")
        elif source_station == destination_station:
            st.error("⚠️ Source and Destination stations cannot be the same.")
        else:
            # 2. Ticket Text Construction
            if need_cab:
                ticket_text = (
                    f"UNIFIED TICKET\n"
                    f"-------------------------\n"
                    f"ID       : {ticket_id}\n"
                    f"Passenger: {passenger_name}\n"
                    f"-------------------------\n"
                    f"METRO: {source_station} -> {destination_station} (₹{metro_fare})\n"
                    f"-------------------------\n"
                    f"CAB ({selected_car}): {cab_pickup} -> {cab_drop} (₹{cab_fare})\n"
                    f"-------------------------\n"
                    f"TOTAL: ₹{grand_total}"
                )
            else:
                ticket_text = (
                    f"METRO TICKET\n"
                    f"-------------------------\n"
                    f"ID       : {ticket_id}\n"
                    f"Passenger: {passenger_name}\n"
                    f"-------------------------\n"
                    f"METRO: {source_station} -> {destination_station}\n"
                    f"-------------------------\n"
                    f"TOTAL: ₹{metro_fare}"
                )

            # 3. Output Display
            st.success("✅ Booking Confirmed Successfully")
            
            col_res1, col_res2 = st.columns([1.5, 1])
            
            with col_res1:
                st.text_area("Ticket Receipt", ticket_text, height=200)
                
                st.download_button(
                    label="⬇ Download Details (TXT)",
                    data=ticket_text,
                    file_name=f"Ticket_{ticket_id}.txt",
                    mime="text/plain"
                )
                
            with col_res2:
                qr_bytes = generate_qr_code(ticket_text)
                st.image(qr_bytes, caption="Scan for Entry", width=150)
                
                st.download_button(
                    label="⬇ QR Code (PNG)",
                    data=qr_bytes,
                    file_name=f"Ticket_{ticket_id}.png",
                    mime="image/png"
                )

# ============================================================
# APP ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
