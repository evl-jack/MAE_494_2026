# Portable-package validation — 28 October 2026

The ZIPs were extracted into a separate Windows folder whose path contains spaces. Checks used the existing project Python environment (PyTorch 2.5.1+cpu), rather than a freshly installed environment.

| Check | Result |
| --- | --- |
| Code-only file hashes | Passed |
| Derivative, chain-rule and Hamiltonian fixture checks | Passed; model weights unchanged, zero optimizer updates |
| Training request without the explicit --train flag | Refused as intended |
| Local installation of all three result ZIPs | Passed |
| All archived file hashes before verification scripts | Passed |
| Saved 3D Long22000 and 6D 5U checkpoint queries | Passed |
| Report evidence and headline counts | Passed |
| Completed Experiment 5 training-record verification | Passed; no optimizer updates |
| Saved Experiment 5 metrics and control replay | Passed; no new encounters |

All original scientific files were copied byte for byte and checked against their source hashes. This packaging work performed no training, new reference solve, or reserved 6D final evaluation. The explicit smoke-training command is included for a future user, but was not executed during packaging.

The final ZIP structure and file hashes were checked again after adding this validation note. The original ZIPs remain the integrity reference; some archived verification scripts rewrite verification JSON in an extracted working copy.

## What this does not establish

A clean pip installation and the network downloader were not exercised during the relocation test. The documented CPU installation commands follow the official PyTorch 2.5.1 instructions. Linux and macOS were not tested; macOS is not covered by the documented CPU-wheel recipe. Python and dependencies are not bundled. Packaging validation does not change the report's scientific conclusions or establish a safety guarantee.
