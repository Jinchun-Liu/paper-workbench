# QLR Broad Gate Checklist

- [ ] 10-service calibration completed before full 139-service execution.
- [ ] Calibration confirms raw and guarded P90 fields for every service and horizon.
- [ ] Calibration confirms `metrics.csv` remains unchanged.
- [ ] Calibration report records runtime, memory, disk growth, and any service failures.
- [ ] Full run command is explicitly reviewed after calibration; it is not launched by the planning script.
- [ ] Full run keeps service policy parameters identical to the existing service policy semantics.
- [ ] Full run report preserves mixed/negative outcomes instead of tuning for a better story.
- [ ] Full run does not invoke the held deep-model path.
