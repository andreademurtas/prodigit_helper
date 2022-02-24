## Prodigit Helper
Un tool che vuole rendere più veloce e immediata la prenotazione delle aule su Prodigit.

# Installazione
Alcuni steps sono necessari per l'installazione. Innanzitutto assicurarsi di avere python3.x,pip e git installati, quindi aprire un terminale e clonare la repo:
```bash
git clone https://github.com/andreademurtas/prodigit_helper
```
Una volta fatto ciò, è necessario scaricare il web driver geckodriver, disponibile [qui](https://github.com/mozilla/geckodriver/releases)(fare attenzione a scaricare la vesione giusta per il proprio sistema), e poi estrarlo nella cartella clonata con lo step precedente.
Come ultimo step, spostarsi nella cartella e installare i requirements:
```bash
cd prodigit_helper
pip install -r requirements.txt
```

# Utilizzo
```bash
python3 main.py
```

# Aggiungere i propri corsi
Per aggiungere dei corsi, scrivere a <ypno25@protonmail.com>
