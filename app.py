import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Quantum Random Number Generator",
    page_icon="⚛️",
    layout="centered"
)

# ==========================================
# TITLE
# ==========================================

st.markdown("""
# ⚛️ Quantum Random Number Generator

Generate true quantum randomness using Qiskit
""")

# ==========================================
# BUTTON
# ==========================================

if st.button("🎲 Generate Quantum Bits"):

    # ==========================================
    # CREATE CIRCUIT
    # ==========================================

    qc = QuantumCircuit(1, 1)

    qc.h(0)

    qc.measure(0, 0)

    # ==========================================
    # SHOW CIRCUIT
    # ==========================================

    st.subheader("⚛️ Quantum Circuit Used")

    st.code(qc.draw(output='text'))

    # ==========================================
    # RUN SIMULATOR
    # ==========================================

    simulator = AerSimulator()

    job = simulator.run(
        qc,
        shots=100,
        memory=True
    )

    result = job.result()

    memory = result.get_memory()

    random_bits = ''.join(memory)

    # ==========================================
    # COUNT BITS
    # ==========================================

    zeros = random_bits.count('0')

    ones = random_bits.count('1')

    # ==========================================
    # DISPLAY RANDOM BITS
    # ==========================================

    st.subheader("Generated Quantum Bitstream")

    st.code(random_bits)

    # ==========================================
    # STATS
    # ==========================================

    col1, col2 = st.columns(2)

    col1.metric("Zeros", zeros)

    col2.metric("Ones", ones)

    # ==========================================
    # HISTOGRAM
    # ==========================================

    fig, ax = plt.subplots()

    ax.bar(
        ['0', '1'],
        [zeros, ones]
    )

    ax.set_title("Bit Distribution")

    ax.set_xlabel("Bit")

    ax.set_ylabel("Count")

    st.pyplot(fig)

    # ==========================================
    # SUCCESS
    # ==========================================

    st.success("✅ Quantum randomness generated successfully!")
