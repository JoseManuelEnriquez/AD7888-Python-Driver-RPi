# RPi Battery Monitor (AD7888)

Monitor del nivel de batería para Raspberry Pi mediante un ADC externo **AD7888** conectado por SPI. Lee la tensión de la batería, la convierte a porcentaje de carga y permite actuar ante niveles bajos (avisos, registro o apagado seguro).

> Raspberry Pi no tiene entradas analógicas, por lo que se usa un ADC de 12 bits externo para medir la tensión de la batería de forma fiable.

---

## Características

- Lectura de tensión de batería vía SPI con el AD7888 (12 bits).
- Conversión de tensión a porcentaje de carga mediante curva configurable.
- Promediado de muestras para reducir ruido.
- Umbrales configurables de aviso y de apagado crítico.
- Registro de lecturas (consola y/o fichero).
- Ejecución como servicio `systemd` al arrancar.

> Ajusta esta lista a lo que haga realmente tu código.

---

## Hardware necesario

| Componente | Notas |
|---|---|
| Raspberry Pi | Cualquier modelo con SPI y cabecera de 40 pines |
| AD7888 | ADC de 12 bits, 8 canales, interfaz SPI |
| Divisor resistivo | Adapta la tensión de la batería al rango del ADC |
| Batería | Indica tipo y tensión (p. ej. Li-ion 1S, 3.0–4.2 V) |
| Condensador de desacoplo | 100 nF cerca de VDD del AD7888 |

### Divisor de tensión

La entrada del ADC no debe superar su tensión de referencia / alimentación. Calcula el divisor según tu batería:

```
V_ADC = V_BAT × R2 / (R1 + R2)
```

Valores usados en este proyecto: `R1 = ___ kΩ`, `R2 = ___ kΩ`.

---

## Conexiones

| AD7888 | Raspberry Pi | Pin físico |
|---|---|---|
| VDD | 3.3 V | 1 |
| GND | GND | 6 |
| DIN | MOSI (GPIO10) | 19 |
| DOUT | MISO (GPIO9) | 21 |
| SCLK | SCLK (GPIO11) | 23 |
| CS | CE0 (GPIO8) | 24 |
| AINx | Salida del divisor | — |

> Verifica el pinout contra tu código y el datasheet. Canal del ADC usado para la batería: `AIN_` (ajústalo).

---

## Requisitos de software

- Raspberry Pi OS (o compatible)
- Python 3.9+
- SPI habilitado

Habilitar SPI:

```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

Comprobar que existe el dispositivo:

```bash
ls /dev/spidev0.*
```

---

## Instalación

```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencias típicas: `spidev`.

---

## Configuración

Edita los parámetros en `config.py` (o en el fichero de configuración que uses):

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `SPI_BUS` | Bus SPI | `0` |
| `SPI_DEVICE` | Chip select | `0` |
| `SPI_SPEED_HZ` | Frecuencia SPI | `1000000` |
| `ADC_CHANNEL` | Canal AD7888 conectado al divisor | `0` |
| `VREF` | Tensión de referencia del ADC (V) | `2.5` |
| `DIVIDER_RATIO` | `(R1 + R2) / R2` | `2.0` |
| `NUM_SAMPLES` | Muestras a promediar | `16` |
| `SAMPLE_INTERVAL_S` | Intervalo entre medidas (s) | `10` |
| `V_FULL` | Tensión de batería al 100 % | `4.2` |
| `V_EMPTY` | Tensión de batería al 0 % | `3.0` |
| `V_WARN` | Umbral de aviso | `3.4` |
| `V_CRITICAL` | Umbral de apagado seguro | `3.2` |

> Los valores son orientativos: sustitúyelos por los de tu código real.

---

## Uso

```bash
python3 main.py
```

Ejemplo de salida:

```
[2026-10-28 12:00:00] V_BAT = 3.92 V | Nivel = 76 %
[2026-10-28 12:00:10] V_BAT = 3.91 V | Nivel = 75 %
[2026-10-28 12:00:20] V_BAT = 3.40 V | Nivel = 33 % | ⚠ BATERÍA BAJA
```

---

## Cómo funciona

1. El código abre el bus SPI y configura el AD7888 para seleccionar el canal de la batería.
2. Se toman `NUM_SAMPLES` lecturas de 12 bits (0–4095) y se promedian.
3. Se convierte el valor a tensión:

   ```
   V_ADC = (código / 4096) × VREF
   V_BAT = V_ADC × DIVIDER_RATIO
   ```

4. La tensión se transforma en porcentaje interpolando entre `V_EMPTY` y `V_FULL` (o mediante una tabla de descarga).
5. Si la tensión cae por debajo de `V_WARN` se emite un aviso; por debajo de `V_CRITICAL` se puede lanzar un apagado seguro (`sudo shutdown -h now`).

---

## Ejecución como servicio (systemd)

Crea `/etc/systemd/system/battery-monitor.service`:

```ini
[Unit]
Description=RPi Battery Monitor (AD7888)
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/<repositorio>/.venv/bin/python /home/pi/<repositorio>/main.py
WorkingDirectory=/home/pi/<repositorio>
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now battery-monitor.service
journalctl -u battery-monitor.service -f
```

---

## Estructura del proyecto

```
.
├── main.py            # Bucle principal de monitorización
├── ad7888.py          # Driver SPI del ADC
├── config.py          # Parámetros de configuración
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Calibración y precisión

- Mide la tensión real de la batería con un multímetro y compárala con la lectura para ajustar `DIVIDER_RATIO`.
- Usa resistencias del 1 % o mejor en el divisor.
- La curva de descarga de una batería no es lineal: para más precisión usa una tabla tensión–porcentaje específica de tu química.
- La tensión varía con la carga; mide en condiciones de uso representativas.

---

## Solución de problemas

| Problema | Posible causa |
|---|---|
| `FileNotFoundError: /dev/spidev0.0` | SPI no habilitado |
| Lecturas siempre 0 o 4095 | Cableado erróneo, CS incorrecto o divisor mal dimensionado |
| Lecturas ruidosas | Falta desacoplo en VDD, cables largos, pocas muestras promediadas |
| Valores desplazados | `VREF` o `DIVIDER_RATIO` incorrectos |

---

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE). Consulta el fichero `LICENSE` para más detalles.

## Autor

José — [embeddedbyjose.com](https://embeddedbyjose.com) · [GitHub](https://github.com/JoseManuelEnriquez)