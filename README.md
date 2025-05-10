# PHY-Security

## Overview

This project demonstrates a physical-layer security implementation using three Python scripts: `send.py`, `receive.py`, and `eve.py`, which represent the transmitter, receiver, and eavesdropper nodes respectively. These scripts are deployed on three separate Raspberry Pi devices.

- `send.py`: Generates, modulates, and transmits the signal (runs on Raspberry Pi 1).
- `receive.py`: Receives and demodulates the signal (runs on Raspberry Pi 2).
- `eve.py`: Attempts to intercept and demodulate the signal without access to the secret parameters (runs on Raspberry Pi 3).

## Methodology

1. A bit sequence of size 10 is generated for simplicity (configurable).
2. A random bitstream is created using Python’s built-in libraries.
3. During transmission, a phase shift is applied to the modulation scheme based on a shared secret between the transmitter and the legitimate receiver.
4. Variable Phase Shift Keying (PSK) is used to enhance security by mapping different bits to modulation symbols.
5. Data is broadcast using socket communication, allowing all receivers to capture it — but only the legitimate receiver knows how to decode it.
6. The legitimate receiver decodes the original message, while the eavesdropper receives unintelligible data due to unknown phase shifts and modulation schemes.

---

*This project illustrates how security can be implemented at the physical layer by leveraging shared modulation secrets.*
