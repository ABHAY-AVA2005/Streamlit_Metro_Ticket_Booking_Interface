# ============================================================
# METRO + CAB TICKET BOOKING APPLICATION (STREAMLIT)
# ============================================================
# Features:
# 1. Metro ticket booking with passenger count
# 2. Optional cab booking for last-mile travel
# 3. Automatic fare calculation (Metro + Cab)
# 4. QR code generation containing full ticket details
# 5. Immediate bill / ticket display after booking
# 6. Ticket download as QR image
# ============================================================


# ---------------- IMPORTS ----------------
import streamlit as st          # Streamlit UI framework
import qrcode                   # QR code generation
from io import BytesIO          # In-memory byte stream handling
import uuid                     # Unique booking ID generator


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Metro and Cab Booking",
    layout="centered"
)


# ============================================================
# CONSTANTS (FARE & LOCATIONS)
# ============================================================

METRO_PRICE = 30        # Fixed fare per passenger for Metro
CAB_PRICE = 50          # Fixed fare per passenger for Cab

STATIONS = [
    "Ameerpet",
    "KPHB",
    "Kukatpally",
    "Madhapur",
    "Hitech City",
    "Raidurg"
]

LOCATIONS = [
    "Office",
    "Home",
    "Shopping Mall",
    "Hospital",
    "College",
    "Hotel"
]


# ============================================================
# FUNCTION: GENERATE QR CODE
# ============================================================
def generate_qr_code(ticket_text: str) -> BytesIO:
    """
    Generates a QR code image from ticket text.
    Returns the QR image as a BytesIO object (PNG format),
    which Streamlit can display or allow for download.
    """
    qr = qrcode.QRCode(
        version=1,        # Controls QR size
        box_size=8,       # Pixel size of each box
        border=4          # Border thickness
    )
    qr.add_data(ticket_text)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


# ============================================================
# SESSION STATE (TO REMEMBER CAB SELECTION)
# ============================================================
if "show_cab_details" not in st.session_state:
    st.session_state.show_cab_details = False


# ============================================================
# MAIN APPLICATION
# ============================================================
def main():

    # ---------------- TITLE ----------------
    st.title("🚇 Metro and Cab Booking System")

    # ---------------- PASSENGER DETAILS ----------------
    passenger_name = st.text_input("Passenger Full Name")
    st.markdown("---")

    # ---------------- METRO DETAILS ----------------
    st.header("1. Metro Details")

    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Source Station", STATIONS)
    with col2:
        destination = st.selectbox("Destination Station", STATIONS, index=1)

    # Number of passengers (tickets)
    passenger_count = st.number_input(
        "Number of Passengers",
        min_value=1,
        value=1,
        step=1
    )

    # Metro fare calculation
    metro_fare = passenger_count * METRO_PRICE
    st.info(f"🚇 Metro Fare: ₹{metro_fare}")

    st.markdown("---")

    # ---------------- CAB REQUIREMENT ----------------
    st.header("2. Cab Requirement")
    st.write("Do you need a cab for last-mile connectivity?")

    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("YES"):
            st.session_state.show_cab_details = True
    with col_no:
        if st.button("NO"):
            st.session_state.show_cab_details = False

    # Default cab values
    cab_pickup = "N/A"
    cab_drop = "N/A"
    cab_fare = 0

    # ---------------- CAB DETAILS ----------------
    if st.session_state.show_cab_details:
        st.subheader("Cab Booking Details")

        # Pickup is automatically metro destination
        cab_pickup = destination
        st.text_input(
            "Pickup Location",
            value=cab_pickup,
            disabled=True
        )

        # Drop location selection
        cab_drop = st.selectbox("Drop Location", LOCATIONS)

        # Cab fare calculation (same logic as metro)
        cab_fare = passenger_count * CAB_PRICE
        st.info(f"🚕 Cab Fare: ₹{cab_fare}")
    else:
        st.write("Cab Booking: ❌ Not Selected")

    # ---------------- FINAL BILL ----------------
    st.markdown("---")
    grand_total = metro_fare + cab_fare
    st.markdown(f"### 💰 Grand Total: ₹{grand_total}")

    # Button text based on selection
    button_label = (
        "Book Metro & Cab"
        if st.session_state.show_cab_details
        else "Book Metro Only"
    )

    # Placeholder to show ticket immediately after booking
    ticket_placeholder = st.empty()

    # ---------------- BOOKING ACTION ----------------
    if st.button(button_label, type="primary"):

        # -------- VALIDATION --------
        if passenger_name.strip() == "":
            st.error("Passenger name is required.")
            return

        if source == destination:
            st.error("Source and destination cannot be the same.")
            return

        booking_id = str(uuid.uuid4())[:8].upper()

        # -------- TICKET TEXT --------
        if st.session_state.show_cab_details:
            ticket_text = (
                f"UNIFIED METRO + CAB TICKET\n"
                f"=============================\n"
                f"Booking ID : {booking_id}\n"
                f"Passenger  : {passenger_name}\n\n"
                f"METRO : {source} -> {destination}\n"
                f"CAB   : {cab_pickup} -> {cab_drop}\n\n"
                f"Passengers : {passenger_count}\n"
                f"Total Fare : ₹{grand_total}\n"
                f"============================="
            )
            st.success("✅ Metro + Cab Booking Confirmed!")
        else:
            ticket_text = (
                f"METRO TICKET\n"
                f"=============================\n"
                f"Booking ID : {booking_id}\n"
                f"Passenger  : {passenger_name}\n\n"
                f"Route : {source} -> {destination}\n"
                f"Passengers : {passenger_count}\n"
                f"Total Fare : ₹{metro_fare}\n"
                f"============================="
            )
            st.success("✅ Metro Booking Confirmed!")

        # -------- IMMEDIATE TICKET DISPLAY --------
        with ticket_placeholder.container():
            st.markdown("## 🧾 Ticket / Bill Details")
            st.text(ticket_text)

            qr_img = generate_qr_code(ticket_text)
            st.image(qr_img, width=200)

            st.download_button(
                label="⬇ Download Ticket (QR)",
                data=qr_img,
                file_name=f"Ticket_{booking_id}.png",
                mime="image/png"
            )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
