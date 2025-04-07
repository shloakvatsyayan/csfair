import streamlit as st
import socket

# Persistent connection variables
if "sock" not in st.session_state:
    st.session_state.sock = None
    st.session_state.sock_file = None

# Sidebar connection settings
st.sidebar.title("EV3 Connection")

# Input for IP and Port
server_ip = st.sidebar.text_input("Server IP", "192.168.137.3")
server_port = st.sidebar.number_input("Server Port", 1234, step=1)

# Connect Button
if st.sidebar.button("🔌 Connect to EV3"):
    try:
        st.session_state.sock = socket.create_connection((server_ip, server_port), timeout=3)
        st.session_state.sock_file = st.session_state.sock.makefile("rwb", buffering=0)
        st.sidebar.success("✅ Connected to EV3!")
    except Exception as e:
        st.session_state.sock = None
        st.session_state.sock_file = None
        st.sidebar.error(f"Connection failed: {e}")

# Disconnect Button
if st.sidebar.button("❌ Disconnect"):
    if st.session_state.sock:
        try:
            st.session_state.sock.close()
        except Exception:
            pass
    st.session_state.sock = None
    st.session_state.sock_file = None
    st.sidebar.info("🔌 Disconnected.")
# Function to send command
def send_command(cmd: str):
    f = st.session_state.sock_file
    if not f:
        return "Not connected."
    try:
        f.write((cmd + "\n").encode("utf-8"))
        f.flush()
        response = st.session_state.sock.recv(1024).decode("utf-8").strip()
        return response
    except Exception as e:
        return f"Communication error: {e}"

st.title("EV3 Remote Control Panel")

if st.session_state.get("sock"):
    st.success(f"Connected to {server_ip}:{server_port}")
else:
    st.warning("⚠️ Not connected to EV3. Commands will not be sent.")


st.header("Motor A Control")
speed_a = st.number_input("Motor A Speed", value=1000)
angle_a = st.number_input("Motor A Angle", value=90)
if st.button("Send to Motor A"):
    cmd = f"m1 {speed_a} {angle_a}"
    st.success(send_command(cmd))

# --- Motor B Control ---
st.header("Motor B Control")
speed_b = st.number_input("Motor B Speed", value=200)
angle_b = st.number_input("Motor B Angle", value=90)
if st.button("Send to Motor B"):
    cmd = f"m2 {speed_b} {angle_b}"
    st.success(send_command(cmd))

# --- DC Control ---
st.header("Direct Duty Cycle Control")

# --- Motor A DC Control + Stop ---
# --- Motor A DC Control + Stop ---
st.subheader("Motor A Control")
dc_a = st.slider("Motor A DC", -100, 100, 0)
if st.button("Apply DC to Motor A"):
    st.success(send_command(f"dc {dc_a} 0"))

if st.button("🛑 Stop Motor A"):
    st.warning(send_command("es m1"))

# --- Motor B DC Control + Stop ---
st.subheader("Motor B Control")
dc_b = st.slider("Motor B DC", -100, 100, 0)
if st.button("Apply DC to Motor B"):
    st.success(send_command(f"dc 0 {dc_b}"))

if st.button("🛑 Stop Motor B"):
    st.warning(send_command("es m2"))



# --- Stop All Motors ---
st.markdown("### 🚨 Stop All Motors")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='padding:10px;border-radius:5px'>", unsafe_allow_html=True)
        if st.button("🛑 Stop All"):
            out = send_command("es all")
            st.warning(f"All Motors: {out}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Terminate Program ---
st.markdown("### ❌ Terminate Program")
st.markdown("<div style='padding:10px;border-radius:5px'>", unsafe_allow_html=True)
if st.button("💣 Terminate EV3 Program"):
    result = send_command("es all")
    st.error(f"Terminate command sent: {result}")
st.markdown("</div>", unsafe_allow_html=True)


# --- Sensor Queries ---
st.header("Sensor Queries")

if st.button("Get Tilt Sensor Value"):
    st.info(send_command("sq tilt"))