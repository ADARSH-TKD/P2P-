import streamlit as st
import socket
import threading
import time
import queue

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'socket_obj' not in st.session_state:
    st.session_state.socket_obj = None
if 'connection' not in st.session_state:
    st.session_state.connection = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = queue.Queue()
if 'server_thread' not in st.session_state:
    st.session_state.server_thread = None
if 'client_thread' not in st.session_state:
    st.session_state.client_thread = None

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket and connect to a remote address to find local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def server_listener():
    """Thread function to handle server connections and messages"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = get_local_ip()
        port = 7634
        
        s.bind((host, port))
        s.listen(1)
        st.session_state.socket_obj = s
        
        # Wait for connection
        conn, addr = s.accept()
        st.session_state.connection = conn
        st.session_state.connected = True
        st.session_state.message_queue.put(f"✅ Connected to client: {addr[0]}:{addr[1]}")
        
        # Listen for messages
        while st.session_state.connected:
            try:
                data = conn.recv(1024)
                if not data:
                    st.session_state.message_queue.put("❌ Client disconnected")
                    st.session_state.connected = False
                    break
                
                message = data.decode()
                st.session_state.message_queue.put(f"📨 Client: {message}")
                
            except socket.error:
                st.session_state.message_queue.put("❌ Connection lost")
                st.session_state.connected = False
                break
                
    except Exception as e:
        st.session_state.message_queue.put(f"❌ Server error: {str(e)}")
        st.session_state.connected = False

def client_connector(host, port):
    """Thread function to handle client connection and messages"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        st.session_state.socket_obj = s
        st.session_state.connected = True
        st.session_state.message_queue.put(f"✅ Connected to server: {host}:{port}")
        
        # Listen for messages
        while st.session_state.connected:
            try:
                data = s.recv(1024)
                if not data:
                    st.session_state.message_queue.put("❌ Server disconnected")
                    st.session_state.connected = False
                    break
                
                message = data.decode()
                st.session_state.message_queue.put(f"📨 Server: {message}")
                
            except socket.error:
                st.session_state.message_queue.put("❌ Connection lost")
                st.session_state.connected = False
                break
                
    except Exception as e:
        st.session_state.message_queue.put(f"❌ Client error: {str(e)}")
        st.session_state.connected = False

def cleanup_connections():
    """Clean up socket connections"""
    st.session_state.connected = False
    
    if st.session_state.connection:
        try:
            st.session_state.connection.close()
        except:
            pass
        st.session_state.connection = None
    
    if st.session_state.socket_obj:
        try:
            st.session_state.socket_obj.close()
        except:
            pass
        st.session_state.socket_obj = None

def send_message(message):
    """Send message to the connected peer"""
    if st.session_state.connected:
        try:
            if st.session_state.mode == "server" and st.session_state.connection:
                st.session_state.connection.send(message.encode())
                st.session_state.message_queue.put(f"📤 You: {message}")
            elif st.session_state.mode == "client" and st.session_state.socket_obj:
                st.session_state.socket_obj.send(message.encode())
                st.session_state.message_queue.put(f"📤 You: {message}")
        except Exception as e:
            st.session_state.message_queue.put(f"❌ Failed to send message: {str(e)}")

# Streamlit UI
st.title("🌐 Network Chat App")
st.markdown("Connect two devices on the same network for real-time messaging")

# Mode selection
if st.session_state.mode is None:
    st.subheader("Choose your role:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🖥️ Be Server", use_container_width=True):
            st.session_state.mode = "server"
            st.rerun()
    
    with col2:
        if st.button("📱 Be Client", use_container_width=True):
            st.session_state.mode = "client"
            st.rerun()

# Server mode
elif st.session_state.mode == "server":
    st.subheader("🖥️ Server Mode")
    
    local_ip = get_local_ip()
    st.info(f"🌐 Your server IP: **{local_ip}:7634**\n\nShare this IP with the client to connect!")
    
    if not st.session_state.connected and st.session_state.server_thread is None:
        if st.button("🚀 Start Server"):
            st.session_state.server_thread = threading.Thread(target=server_listener, daemon=True)
            st.session_state.server_thread.start()
            st.success("Server started! Waiting for client connection...")
            st.rerun()
    
    if st.session_state.connected:
        st.success("✅ Client connected!")
        
        # Message input
        message = st.text_input("Enter your message:", key="server_message")
        if st.button("Send Message") and message:
            send_message(message)
            st.rerun()

# Client mode
elif st.session_state.mode == "client":
    st.subheader("📱 Client Mode")
    
    if not st.session_state.connected and st.session_state.client_thread is None:
        server_ip = st.text_input("Enter server IP address:", placeholder="192.168.1.100")
        
        if st.button("🔗 Connect to Server") and server_ip:
            st.session_state.client_thread = threading.Thread(
                target=client_connector, 
                args=(server_ip, 7634), 
                daemon=True
            )
            st.session_state.client_thread.start()
            st.success("Connecting to server...")
            st.rerun()
    
    if st.session_state.connected:
        st.success("✅ Connected to server!")
        
        # Message input
        message = st.text_input("Enter your message:", key="client_message")
        if st.button("Send Message") and message:
            send_message(message)
            st.rerun()

# Display messages
if st.session_state.mode is not None:
    st.subheader("💬 Messages")
    
    # Process queued messages
    while not st.session_state.message_queue.empty():
        try:
            message = st.session_state.message_queue.get_nowait()
            st.session_state.messages.append(message)
        except queue.Empty:
            break
    
    # Display messages
    if st.session_state.messages:
        for message in st.session_state.messages[-10:]:  # Show last 10 messages
            st.markdown(f"**{message}**")
    else:
        st.info("No messages yet...")
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Messages"):
            st.session_state.messages = []
            st.rerun()
    
    with col3:
        if st.button("❌ Disconnect"):
            cleanup_connections()
            st.session_state.mode = None
            st.session_state.messages = []
            st.session_state.server_thread = None
            st.session_state.client_thread = None
            st.rerun()

# Auto-refresh for real-time updates
if st.session_state.mode is not None:
    time.sleep(1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Tips:**")
st.markdown("- Both devices must be on the same network")
st.markdown("- Start the server first, then connect the client")
st.markdown("- Share the server IP with the client device")
st.markdown("- Click 'Refresh' if messages don't appear immediately")