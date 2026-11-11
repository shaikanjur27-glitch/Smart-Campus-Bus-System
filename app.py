import pandas as pd
import streamlit as st

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(
    page_title="Smart Campus Bus System",
    page_icon="🚌",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .muted {
        color: #64748b;
    }
    .seat-card {
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 9px 3px;
        text-align: center;
        margin: 3px 0;
        background: #f8fafc;
    }
    .seat-id {
        font-size: 1rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SEAT DATA: ALL SEATS ARE REGULAR
# --------------------------------------------------
def create_seats():
    seats = []

    # Left side: 3 seats per row, 11 rows
    for row_number in range(1, 12):
        for letter in ("A", "B", "C"):
            seats.append({
                "id": f"L{row_number}{letter}",
                "row": row_number,
                "side": "Left",
                "status": "Available",
                "user": None,
            })

    # Right side: 2 seats per row, 12 rows
    for row_number in range(1, 13):
        for letter in ("D", "E"):
            seats.append({
                "id": f"R{row_number}{letter}",
                "row": row_number,
                "side": "Right",
                "status": "Available",
                "user": None,
            })

    return pd.DataFrame(seats)


# --------------------------------------------------
# INITIAL DEMO DATA
# --------------------------------------------------
def initialize_data():
    if "users" not in st.session_state:
        st.session_state.users = {
            "STU001": {
                "name": "Amit Kumar",
                "role": "Student",
                "fee_paid": True,
                "stop": "Guntur Junction",
            },
            "STU002": {
                "name": "Sai Kiran",
                "role": "Student",
                "fee_paid": False,
                "stop": "Guntur Junction",
            },
            "DRV999": {
                "name": "Raju (Driver)",
                "role": "Driver",
                "fee_paid": True,
                "stop": None,
            },
            "MGMT01": {
                "name": "Admin Office",
                "role": "Management",
                "fee_paid": True,
                "stop": None,
            },
        }

    if "seats" not in st.session_state:
        st.session_state.seats = create_seats()


# --------------------------------------------------
# BOOKING HELPERS
# --------------------------------------------------
def get_booking(user_id):
    return st.session_state.seats[
        (st.session_state.seats["user"] == user_id)
        & (st.session_state.seats["status"] == "Booked")
    ]


def book_seat(seat_id, user_id):
    seats = st.session_state.seats
    available = (
        (seats["id"] == seat_id)
        & (seats["status"] == "Available")
    )

    if not available.any():
        return False

    st.session_state.seats.loc[available, "status"] = "Booked"
    st.session_state.seats.loc[available, "user"] = user_id
    return True


def cancel_booking(user_id):
    booking = st.session_state.seats["user"] == user_id
    st.session_state.seats.loc[booking, "status"] = "Available"
    st.session_state.seats.loc[booking, "user"] = None


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
def render_login():
    st.header("Welcome to the Smart Campus Bus System")
    st.write(
        "A simple portal to reserve bus seats and manage passenger information."
    )

    with st.expander("How does this application work?", expanded=True):
        st.markdown(
            """
            **Students:** Log in, select an available seat and confirm the booking.

            **Driver:** Log in to view the passenger list and their boarding stops.

            **Management:** Log in to register students, check fee status and monitor bookings.

            Select your account type below and enter your college ID.
            """
        )

    student_tab, driver_tab, management_tab = st.tabs(
        ["🎓 Student", "🚌 Driver", "🏢 Management"]
    )

    with student_tab:
        st.caption("Demo student IDs: STU001 (fee paid), STU002 (fee unpaid)")
        with st.form("student_login"):
            student_id = st.text_input(
                "Student college ID",
                placeholder="Example: STU001",
            ).strip().upper()
            submitted = st.form_submit_button(
                "Login as Student", type="primary", use_container_width=True
            )

        if submitted:
            profile = st.session_state.users.get(student_id)

            if not profile or profile["role"] != "Student":
                st.error("Student ID not found. Please contact the management office.")
            elif not profile["fee_paid"]:
                st.error(
                    "Your transport fee is marked as unpaid. "
                    "Please contact the management office."
                )
            else:
                st.session_state.logged_in_user = student_id
                st.rerun()

    with driver_tab:
        st.caption("Demo driver ID: DRV999")
        with st.form("driver_login"):
            driver_id = st.text_input(
                "Driver ID",
                placeholder="Example: DRV999",
            ).strip().upper()
            submitted = st.form_submit_button(
                "Login as Driver", type="primary", use_container_width=True
            )

        if submitted:
            profile = st.session_state.users.get(driver_id)
            if profile and profile["role"] == "Driver":
                st.session_state.logged_in_user = driver_id
                st.rerun()
            else:
                st.error("Driver ID not found.")

    with management_tab:
        st.caption("Demo management ID: MGMT01")
        with st.form("management_login"):
            management_id = st.text_input(
                "Management ID",
                placeholder="Example: MGMT01",
            ).strip().upper()
            submitted = st.form_submit_button(
                "Login as Management", type="primary", use_container_width=True
            )

        if submitted:
            profile = st.session_state.users.get(management_id)
            if profile and profile["role"] == "Management":
                st.session_state.logged_in_user = management_id
                st.rerun()
            else:
                st.error("Management ID not found.")


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------
def render_student_dashboard(user_id):
    profile = st.session_state.users[user_id]

    st.header("🎓 Student Dashboard")
    st.write(f"Welcome, **{profile['name']}**!")
    st.info(
        f"Your registered boarding stop is **{profile['stop']}**. "
        "You can book one seat at a time."
    )

    booking = get_booking(user_id)

    if not booking.empty:
        seat_id = booking.iloc[0]["id"]
        st.success(f"Your seat is confirmed: **{seat_id}**")

        if st.button("Cancel My Booking"):
            cancel_booking(user_id)
            st.success("Your booking has been cancelled.")
            st.rerun()
        return

    seats = st.session_state.seats
    available_seats = seats[seats["status"] == "Available"]

    col1, col2 = st.columns(2)
    col1.metric("Available seats", len(available_seats))
    col2.metric("Booked seats", int((seats["status"] == "Booked").sum()))

    if available_seats.empty:
        st.error("Sorry, all bus seats are booked.")
        return

    st.subheader("Book your bus seat")
    st.write("Follow these three simple steps:")

    st.markdown(
        """
        1. Select any available seat from the list.
        2. Check the seat number.
        3. Click **Confirm My Booking**.
        """
    )

    chosen_seat = st.selectbox(
        "Select an available seat",
        available_seats["id"].tolist(),
        help="Only seats that are currently available are displayed.",
    )

    if st.button("Confirm My Booking", type="primary"):
        if book_seat(chosen_seat, user_id):
            st.success(
                f"Booking successful! Your seat number is **{chosen_seat}**."
            )
            st.rerun()
        else:
            st.error("This seat has just been booked. Please select another seat.")


# --------------------------------------------------
# DRIVER DASHBOARD
# --------------------------------------------------
def render_driver_dashboard():
    st.header("🚌 Driver Dashboard")
    st.write("View the list of students who have reserved seats on the bus.")

    seats = st.session_state.seats
    booked_seats = seats[seats["status"] == "Booked"].copy()

    col1, col2 = st.columns(2)
    col1.metric("Total passengers booked", len(booked_seats))
    col2.metric("Seats still available", int((seats["status"] == "Available").sum()))

    st.subheader("Passenger List")

    if booked_seats.empty:
        st.info("No passengers have booked seats yet.")
        return

    passenger_rows = []

    for _, seat in booked_seats.iterrows():
        user_id = seat["user"]
        profile = st.session_state.users.get(user_id, {})

        passenger_rows.append({
            "Seat number": seat["id"],
            "Student ID": user_id,
            "Passenger name": profile.get("name", "Not registered"),
            "Boarding stop": profile.get("stop", "Not available"),
        })

    passenger_df = pd.DataFrame(passenger_rows)
    st.dataframe(
        passenger_df,
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Passengers by Boarding Stop")
    student_stops = [
        row["Boarding stop"]
        for row in passenger_rows
        if row["Boarding stop"] not in (None, "Not available")
    ]

    if student_stops:
        st.bar_chart(pd.Series(student_stops).value_counts())


# --------------------------------------------------
# MANAGEMENT DASHBOARD
# --------------------------------------------------
def render_management_dashboard():
    st.header("🏢 Management Dashboard")
    st.write("Manage student records and monitor bus seat reservations.")

    seats = st.session_state.seats
    total_seats = len(seats)
    booked = int((seats["status"] == "Booked").sum())
    available = total_seats - booked

    col1, col2, col3 = st.columns(3)
    col1.metric("Total bus seats", total_seats)
    col2.metric("Seats booked", booked)
    col3.metric("Seats available", available)

    st.progress(booked / total_seats if total_seats else 0)
    st.caption(f"Bus occupancy: {booked} out of {total_seats} seats.")

    st.divider()
    st.subheader("Register or Update Student")

    with st.form("student_registration"):
        student_id = st.text_input(
            "Student college ID",
            placeholder="Example: STU003",
        ).strip().upper()

        student_name = st.text_input(
            "Student full name",
            placeholder="Enter full name",
        ).strip()

        boarding_stop = st.text_input(
            "Boarding stop",
            placeholder="Example: Guntur Junction",
        ).strip()

        fee_paid = st.checkbox("Transport fee paid")
        submitted = st.form_submit_button("Save Student Details", type="primary")

    if submitted:
        if not student_id or not student_name or not boarding_stop:
            st.error("Please enter the student ID, name and boarding stop.")
        elif (
            student_id in st.session_state.users
            and st.session_state.users[student_id]["role"] != "Student"
        ):
            st.error("This ID belongs to a driver or management account.")
        else:
            st.session_state.users[student_id] = {
                "name": student_name,
                "role": "Student",
                "fee_paid": fee_paid,
                "stop": boarding_stop,
            }
            st.success(f"Student details saved for {student_name}.")
            st.rerun()

    st.divider()
    st.subheader("Student Records")

    records = []

    for student_id, profile in st.session_state.users.items():
        if profile["role"] != "Student":
            continue

        booking = get_booking(student_id)
        seat_number = booking.iloc[0]["id"] if not booking.empty else "Not booked"

        records.append({
            "Student ID": student_id,
            "Name": profile["name"],
            "Boarding stop": profile["stop"],
            "Transport fee": "Paid" if profile["fee_paid"] else "Unpaid",
            "Seat": seat_number,
        })

    if records:
        st.dataframe(
            pd.DataFrame(records),
            hide_index=True,
            use_container_width=True,
        )


# --------------------------------------------------
# VISUAL BUS SEAT MAP
# --------------------------------------------------
def render_seat_map():
    st.divider()
    st.subheader("🗺️ Bus Seat Layout")
    st.write("Green means available. Red means booked.")

    st.markdown("🟩 **Available**     🟥 **Booked**")
    st.caption(
        "L = Left side of bus | R = Right side of bus | "
        "Number = Row | Letter = Seat"
    )

    seats = st.session_state.seats

    st.markdown("**FRONT OF BUS**")

    for row_number in range(1, 13):
        left = seats[
            (seats["side"] == "Left") & (seats["row"] == row_number)
        ]
        right = seats[
            (seats["side"] == "Right") & (seats["row"] == row_number)
        ]

        columns = st.columns([1, 1, 1, 0.35, 1, 1])

        for index, (_, seat) in enumerate(left.iterrows()):
            symbol = "🟥" if seat["status"] == "Booked" else "🟩"
            columns[index].markdown(
                f"<div class='seat-card'>{symbol}<br>"
                f"<span class='seat-id'>{seat['id']}</span></div>",
                unsafe_allow_html=True,
            )

        columns[3].markdown(
            "<div style='text-align:center;padding-top:15px;'>│</div>",
            unsafe_allow_html=True,
        )

        for index, (_, seat) in enumerate(right.iterrows()):
            symbol = "🟥" if seat["status"] == "Booked" else "🟩"
            columns[index + 4].markdown(
                f"<div class='seat-card'>{symbol}<br>"
                f"<span class='seat-id'>{seat['id']}</span></div>",
                unsafe_allow_html=True,
            )

    st.markdown("**REAR OF BUS**")

    with st.expander("How to understand seat numbers"):
        st.markdown(
            """
            - **L2A** means left side, second row, seat A.
            - **L2B** means left side, second row, seat B.
            - **R3D** means right side, third row, seat D.
            - The empty middle space represents the bus aisle.
            """
        )


# --------------------------------------------------
# MAIN APP
# --------------------------------------------------
initialize_data()

st.markdown(
    "<div class='main-title'>🚌 Smart Campus Bus Management System</div>"
    "<div class='muted'>Simple bus seat booking and passenger management portal</div>",
    unsafe_allow_html=True,
)

if "logged_in_user" not in st.session_state:
    render_login()

else:
    user_id = st.session_state.logged_in_user
    profile = st.session_state.users.get(user_id)

    if profile is None:
        del st.session_state.logged_in_user
        st.rerun()

    st.sidebar.title("My Account")
    st.sidebar.success(profile["name"])
    st.sidebar.write(f"**Account type:** {profile['role']}")

    if st.sidebar.button("Logout", use_container_width=True):
        del st.session_state.logged_in_user
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption(
        "If your college ID or transport-fee details are incorrect, "
        "please contact the management office."
    )

    if profile["role"] == "Student":
        render_student_dashboard(user_id)

    elif profile["role"] == "Driver":
        render_driver_dashboard()

    elif profile["role"] == "Management":
        render_management_dashboard()

    render_seat_map()

st.caption(
    "Demonstration version. Data is stored temporarily during the current "
    "Streamlit session. Connect a database and secure authentication before "
    "using this system with real student information."
)
