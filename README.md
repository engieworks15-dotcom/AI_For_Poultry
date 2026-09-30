# PoultryGrid AI

A small neural network that judges the condition of a poultry nursery from its sensor readings, and a Raspberry Pi controller that uses that judgement to set the ventilation fan speed.

The AI classifies the nursery as **Healthy**, **Warning** or **Critical**. Ventilation has a large effect on gas build-up, humidity and temperature, so the fan runs at one of three speeds depending on the result.

> **Status: prototype.** The model is currently trained on synthetic data generated from hand-written rules. It has not yet been trained or tested on real nursery readings. See [Limitations](#limitations).

## How it works

```
 sensors ──► inference_service.py ──► condition file (RAM) ──► fan_controller.py ──► fan
 (DHT22, MQ-135,    loads the model        /dev/shm/                  3 speed levels,
  LDR, fan tach)    once, predicts         poultry_condition.json     anti-flapping logic
                    every 5 seconds
```

The fan's measured RPM is also an input to the model, so the AI sees the effect of its own ventilation decisions.

Scope: the AI controls the **nursery only**. The incubator above it is isolated and runs on its own standard incubator controller.

## Inputs and outputs

| Input | Sensor | Notes |
|---|---|---|
| `humidity` | DHT22 | % relative humidity |
| `gas_index` | MQ-135 | Relative index (0 = clean-air baseline). **Not ppm**, and not ammonia-specific |
| `temperature` | DHT22 | °C |
| `light` | LDR on LM393 board | Relative brightness, not lux |
| `fan_rpm` | Fan tach wire | From a 3-wire 12 V computer fan |

The feature order is fixed everywhere: `humidity, gas_index, temperature, light, fan_rpm`.

| Output | Meaning | Fan level |
|---|---|---|
| 0 Healthy | Conditions are fine | Low |
| 1 Warning | Something is drifting | Medium |
| 2 Critical | Immediate problem | High |

The model is a small PyTorch network: 5 inputs → 16 → 16 → 3 classes.

## Repository layout

```
EnvironmentDataset.py     Generates the synthetic training data (12,000 rows)
model.py                  Trains the model; prints train vs test accuracy
results.py                Makes the four presentation charts
coop_environmental_data.csv
pi/
  config.py               All settings in one place (pins, fan levels, timings)
  sensors.py              Reads the sensors (SIMULATE=1 for fake readings)
  inference_service.py    Loads the model, predicts, writes the condition
  fan_controller.py       Reads the condition, sets the fan speed
  export_scaler.py        Converts the scaler for use on the Pi
  systemd/                Services that start both scripts at boot
```

## Training (on your computer)

```bash
pip install torch scikit-learn pandas numpy joblib matplotlib seaborn
python EnvironmentDataset.py    # creates coop_environmental_data.csv
python model.py                 # trains; saves offline_env_model.pth and sensor_scaler.pkl
python results.py               # optional: saves the four charts
python pi/export_scaler.py      # creates scaler.json for the Pi
```

`model.py` prints train accuracy, test accuracy and the gap between them. A gap under 1 to 2 points is healthy. A gap above about 5 points suggests overfitting.

Retrain (and re-export the scaler) whenever you change the data or the feature list. The model and scaler must always come from the same training run.

### Results so far

On the original 4,000-row dataset the model scored about 95 to 96% on the held-out test set. Most errors were readings close to a rule threshold. Growing the dataset to 12,000 rows is expected to raise this and shrink the train/test gap, but that number has not been recorded yet.

## Deploying to the Raspberry Pi

1. Copy the `pi/` folder, `offline_env_model.pth` and `scaler.json` to the Pi (for example `/home/pi/poultrygrid`).
2. Create a virtual environment and install the dependencies:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install torch numpy gpiozero adafruit-circuitpython-dht adafruit-circuitpython-ads1x15
   ```
3. Test without hardware, in two terminals:
   ```bash
   SIMULATE=1 python inference_service.py
   SIMULATE=1 python fan_controller.py
   ```
4. Edit the user name and paths in `pi/systemd/*.service` if they differ, then install the services:
   ```bash
   sudo cp systemd/*.service /etc/systemd/system/
   sudo systemctl enable --now poultry-inference poultry-fan
   ```
5. Watch the logs with `journalctl -u poultry-inference -f` and `journalctl -u poultry-fan -f`.

### Wiring (defaults in `config.py`)

| Part | Connection |
|---|---|
| DHT22 | GPIO 4 |
| MQ-135 and LDR | Through an ADS1115 ADC on I2C (channels 0 and 1), because the Pi has no analog inputs |
| Fan PWM | GPIO 18, through a MOSFET or fan driver on a separate 12 V supply |
| Fan tach | GPIO 23, pulled up to **3.3 V** (never 12 V) |

The hardware code has not yet been tested on a real Pi. Check each library's current example before relying on it, and have mains-powered parts (bulbs, heater, humidifier relays) wired by a qualified person.

## Control behaviour

- **Speeds up immediately, slows down slowly.** Because fan RPM is a model input, a faster fan improves the readings, which would otherwise tell the AI to slow down again. The controller needs about 30 seconds of consistently better readings and a 60-second hold before stepping down one level.
- **Cold/dry guard.** If the air is clean but the nursery is cold or dry, more ventilation would make things worse, so the fan stays on low.
- **Failsafe.** At boot, and whenever the AI result is missing, stale or a sensor fails, the fan runs at the medium level.
- **Fan fault warning.** A message is logged if the fan is commanded on but the tach shows it isn't spinning.

## Calibrate before trusting it

These values are placeholders in `config.py` and `sensors.py`:

| Setting | What to do |
|---|---|
| `FAN_DUTY`, `FAN_MAX_RPM` | Measure the real RPM at each duty cycle with the tach. Make sure the training data's RPM range matches your fan |
| `MQ_R0_OHMS` | Measure in clean air after a day or two of burn-in |
| `MQ_DIVIDER_RATIO`, `MQ_LOAD_OHMS` | Match your MQ-135 board and voltage divider |
| `GAS_INDEX_SCALE` | Map the sensor onto the 0 to 50 scale used in training |
| `_light_value` | Flip the calculation if brighter reads as a lower value |
| `TARGET_TEMP` | Set the nursery's ideal temperature (also in `EnvironmentDataset.py`) |

## Safety

The model classifies conditions; it is not a safety system. Keep protection that does not depend on software:

- A hard-wired thermostat that cuts the heater at a maximum temperature.
- Wiring that makes the fan run at full speed if the Pi or a script dies (a low PWM pin otherwise stops the fan).
- A UPS or battery for the fans and the Pi, and the Pi's hardware watchdog enabled.
- An alarm (buzzer or message) when the nursery reaches Critical.

## Limitations

- **Synthetic data.** The labels come from fixed rules applied to the same inputs, and the test set comes from the same generator. The accuracy measures how well the network copies those rules, not how well it judges a real nursery. A plain if/else would score 100% on this data. The AI only adds value once it is trained on real readings labelled by someone who knows the birds.
- **Fixed temperature target.** Chicks need less heat as they grow. The model has no age input, so one target applies throughout.
- **Fan only.** Only ventilation is controlled. Heat (bulbs and heater), humidifier and lighting are not yet driven by the AI.
- **Sensor quality.** The MQ-135 is not ammonia-specific and drifts. The DHT22 is adequate but basic.

## Roadmap

- Log real readings on the Pi and retrain on them.
- Use sensors in pairs, feeding the model the average and flagging disagreement as a sensor fault.
- Upgrade sensors: an electrochemical NH3 sensor, an SHT31 for temperature and humidity, a BH1750 for lux, and possibly an NDIR CO2 sensor.
- Control the heating, bulbs and humidifier, with rules for which device to try first.

## License

MIT. See [LICENSE](LICENSE).
