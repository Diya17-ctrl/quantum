import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
from datetime import datetime, timedelta
import numpy as np
import io

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Quantum Random Number Generator",
    page_icon="⚛️",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    .stMetricLabel {
        font-size: 14px;
        color: #888;
    }
    .header-title {
        font-size: 36px;
        font-weight: bold;
        color: #fff;
        margin-bottom: 5px;
    }
    .header-subtitle {
        font-size: 16px;
        color: #aaa;
    }
    .live-indicator {
        color: #00FF41;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================
if 'bits_generated' not in st.session_state:
    st.session_state.bits_generated = ""
if 'total_bits' not in st.session_state:
    st.session_state.total_bits = 0
    st.session_state.start_time = None
    st.session_state.is_running = False
    st.session_state.bit_chunks = []

# ==========================================
# HEADER
# ==========================================
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<div class="header-title">⚛️ Quantum Random Number Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Generating true random numbers using quantum mechanics</div>', unsafe_allow_html=True)

with col2:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        status = '<span class="live-indicator">● Connected to Quantum Backend</span>'
        st.markdown(status, unsafe_allow_html=True)
    with col_b:
        if st.button("🎲 Generate New", use_container_width=True, key="generate_btn"):
            st.session_state.is_running = True
            st.session_state.bits_generated = ""
            st.session_state.total_bits = 0
            st.session_state.start_time = datetime.now()
            st.session_state.bit_chunks = []

# ==========================================
# MAIN CONTENT
# ==========================================
if st.session_state.is_running:
    # Generate random bits in batches
    simulator = AerSimulator()
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    
    # Generate 10,240 bits like in the screenshot
    total_to_generate = 10240
    bits_per_batch = 256
    
    progress_bar = st.progress(0)
    placeholder = st.empty()
    
    for i in range(0, total_to_generate, bits_per_batch):
        job = simulator.run(qc, shots=bits_per_batch, memory=True)
        result = job.result()
        memory = result.get_memory()
        batch_bits = ''.join(memory)
        
        st.session_state.bits_generated += batch_bits
        st.session_state.total_bits += bits_per_batch
        st.session_state.bit_chunks.append(batch_bits)
        
        progress = min(st.session_state.total_bits / total_to_generate, 1.0)
        progress_bar.progress(progress)
        
        with placeholder.container():
            st.write(f"Generating... {st.session_state.total_bits}/{total_to_generate} bits")
        
        time.sleep(0.1)
    
    progress_bar.empty()
    placeholder.empty()
    st.session_state.is_running = False

# ==========================================
# MAIN LAYOUT
# ==========================================
if st.session_state.total_bits > 0:
    # Calculate elapsed time
    elapsed = datetime.now() - st.session_state.start_time
    elapsed_seconds = elapsed.total_seconds()
    bit_rate = st.session_state.total_bits / elapsed_seconds if elapsed_seconds > 0 else 0
    
    left_col, right_col = st.columns([1.2, 1])
    
    with left_col:
        # ==========================================
        # RANDOM BIT STREAM
        # ==========================================
        st.subheader("Random Bit Stream")
        
        # Format bits in rows of 40 for display
        bits = st.session_state.bits_generated
        bit_rows = [bits[i:i+40] for i in range(0, len(bits), 40)]
        bit_display = "\n".join(bit_rows[:9])  # Show first 9 rows
        
        st.code(bit_display, language="text")
        
        col_pause, col_clear, col_download = st.columns(3)
        with col_pause:
            st.button("⏸ Pause", use_container_width=True, disabled=True)
        with col_clear:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.bits_generated = ""
                st.session_state.total_bits = 0
                st.session_state.bit_chunks = []
                st.session_state.start_time = None
                st.rerun()
        with col_download:
            if st.button("⬇ Download", use_container_width=True):
                st.download_button(
                    label="Download Bits",
                    data=st.session_state.bits_generated,
                    file_name="quantum_bits.txt",
                    mime="text/plain"
                )
        
        # ==========================================
        # LIVE HISTOGRAM
        # ==========================================
        st.subheader("Live Histogram")
        
        # Create histogram data from chunks
        chunk_zeros = []
        chunk_ones = []
        for chunk in st.session_state.bit_chunks:
            chunk_zeros.append(chunk.count('0'))
            chunk_ones.append(chunk.count('1'))
        
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0E1117')
        ax.set_facecolor('#0E1117')
        
        x = np.arange(len(chunk_zeros))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, chunk_zeros, width, label='0 (Zeros)', color='#1E88E5', alpha=0.8)
        bars2 = ax.bar(x + width/2, chunk_ones, width, label='1 (Ones)', color='#E91E63', alpha=0.8)
        
        ax.set_ylabel('Count', color='#888')
        ax.set_xlabel('', color='#888')
        ax.set_ylim(0, max(max(chunk_zeros), max(chunk_ones)) * 1.1)
        
        # Custom x-axis labels
        ax.set_xticks([0, len(chunk_zeros)-1])
        ax.set_xticklabels(['Older', 'Newer'])
        ax.tick_params(colors='#888')
        ax.legend(loc='upper left', framealpha=0.1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        
        st.pyplot(fig, use_container_width=True)
        
        # ==========================================
        # ZEROS AND ONES BREAKDOWN
        # ==========================================
        st.write("**Bit Count Breakdown**")
        
        zeros_total = st.session_state.bits_generated.count('0')
        ones_total = st.session_state.bits_generated.count('1')
        
        # Horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 2), facecolor='#0E1117')
        ax.set_facecolor('#0E1117')
        
        categories = ['0 (Zeros)', '1 (Ones)']
        values = [zeros_total, ones_total]
        colors_bar = ['#1E88E5', '#E91E63']
        
        bars = ax.barh(categories, values, color=colors_bar, alpha=0.9, height=0.5)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 100, bar.get_y() + bar.get_height()/2, 
                   f'{val:,}', va='center', color='#fff', fontweight='bold')
        
        ax.set_xlabel('Count', color='#888')
        ax.tick_params(colors='#888')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        ax.set_xlim(0, max(values) * 1.15)
        
        st.pyplot(fig, use_container_width=True)
    
    with right_col:
        # ==========================================
        # STATISTICS
        # ==========================================
        st.subheader("Statistics")
        
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric("Total Bits Generated", f"{st.session_state.total_bits:,}")
            st.metric("Bit Rate", f"{bit_rate:,.0f} bits/s")
        
        with stat_col2:
            time_str = f"{int(elapsed_seconds//60):02d}:{int(elapsed_seconds%60):02d}"
            st.metric("Generation Time", time_str)
            st.metric("Quantum Source", "Qiskit Simulator")
        
        # ==========================================
        # BIT DISTRIBUTION
        # ==========================================
        st.subheader("Bit Distribution")
        
        zeros = st.session_state.bits_generated.count('0')
        ones = st.session_state.bits_generated.count('1')
        total = zeros + ones
        
        zero_percent = (zeros / total * 100) if total > 0 else 0
        one_percent = (ones / total * 100) if total > 0 else 0
        balance = abs(zero_percent - 50)
        
        # Donut chart
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='#0E1117')
        ax.set_facecolor('#0E1117')
        
        sizes = [zeros, ones]
        colors = ['#1E88E5', '#E91E63']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=['0 (Zeros)', '1 (Ones)'],
            colors=colors,
            autopct='',
            startangle=90,
            explode=explode,
            textprops={'color': '#aaa', 'fontsize': 10}
        )
        
        # Draw donut hole
        centre_circle = patches.Circle((0, 0), 0.70, fc='#0E1117')
        ax.add_artist(centre_circle)
        
        st.pyplot(fig, use_container_width=True)
        
        # Distribution stats
        col_dist1, col_dist2 = st.columns(2)
        with col_dist1:
            st.write(f"**0 (Zeros)** {zeros:,} ({zero_percent:.2f}%)")
            st.write(f"**1 (Ones)** {ones:,} ({one_percent:.2f}%)")
        with col_dist2:
            st.write(f"**Balance** {balance:.2f}%")
        
        # ==========================================
        # QUANTUM CIRCUIT
        # ==========================================
        st.subheader("Quantum Circuit Used")
        
        # Create a custom colored circuit visualization
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0E1117')
        ax.set_facecolor('#0E1117')
        ax.set_xlim(-0.5, 4)
        ax.set_ylim(-0.5, 2)
        ax.axis('off')
        
        # Draw qubit lines
        # q0 line
        ax.plot([0, 3.5], [1.5, 1.5], 'w-', linewidth=2)
        ax.text(-0.3, 1.5, 'q0', fontsize=12, color='#fff', va='center', fontweight='bold')
        
        # c0 line
        ax.plot([0, 3.5], [0.5, 0.5], color='#ff9800', linewidth=2)
        ax.text(-0.3, 0.5, 'c0', fontsize=12, color='#ff9800', va='center', fontweight='bold')
        
        # Draw Hadamard gate (H)
        hadamard_rect = patches.FancyBboxPatch((0.5, 1.25), 0.5, 0.5, 
                                               boxstyle="round,pad=0.05", 
                                               edgecolor='#1E88E5', facecolor='#1E88E5', 
                                               linewidth=2, alpha=0.8)
        ax.add_patch(hadamard_rect)
        ax.text(0.75, 1.5, 'H', fontsize=14, color='#fff', ha='center', va='center', fontweight='bold')
        ax.text(0.75, 0.95, 'Hadamard', fontsize=9, color='#1E88E5', ha='center')
        
        # Draw measurement gate
        measure_rect = patches.FancyBboxPatch((1.8, 1.25), 0.5, 0.5,
                                              boxstyle="round,pad=0.05",
                                              edgecolor='#E91E63', facecolor='#E91E63',
                                              linewidth=2, alpha=0.8)
        ax.add_patch(measure_rect)
        ax.text(2.05, 1.5, 'M', fontsize=14, color='#fff', ha='center', va='center', fontweight='bold')
        ax.text(2.05, 0.95, 'Measure', fontsize=9, color='#E91E63', ha='center')
        
        # Draw connection lines
        ax.plot([1.05, 1.75], [1.5, 1.5], 'w-', linewidth=2)
        ax.plot([2.3, 3.5], [1.5, 1.5], 'w-', linewidth=2)
        
        # Draw classical bit connection
        ax.plot([2.05, 2.05], [1.25, 0.7], color='#ff9800', linewidth=2)
        ax.plot([2.05, 3.2], [0.5, 0.5], color='#ff9800', linewidth=2)
        
        # Add title
        ax.text(1.75, 2.2, '┌───┐┌─┐', fontsize=11, color='#aaa', family='monospace')
        ax.text(1.75, 2.0, 'q: ┤ H ├┤M├', fontsize=11, color='#aaa', family='monospace')
        ax.text(1.75, 1.8, '└───┘└╥┘', fontsize=11, color='#aaa', family='monospace')
        ax.text(1.75, 1.6, 'c: 1/═════╩═', fontsize=11, color='#aaa', family='monospace')
        
        st.pyplot(fig, use_container_width=True)
        
        st.markdown("""
        **How it works:**
        - 🔵 **Hadamard Gate** (H) puts the qubit in superposition
        - 📊 **Measurement** gives 0 or 1 with equal probability
        """)
        
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)

# ==========================================
# INFO SECTION
# ==========================================
st.markdown("---")
st.markdown("""
**Backend:** Qiskit Aer Simulator | **Updated:** Just now
""")
