# GasPro Web 🌐🔥

Aplicació web de càlcul de canonades de gas.
Classificació de gasos per índex de Wobbe (UNE-EN 437:2022) i càlcul hidràulic amb fórmula de Renouard.

## Funcionalitats

- 🔧 **Calculadora de trams**: Calcula diàmetre, tub comercial, pèrdua de càrrega i velocitat
- 🔥 **Classificador de gasos**: Índex de Wobbe, família i grup segons normativa
- 📋 **Catàleg d'aparells**: Gestiona calderes, cuines, escalfadors
- 🔧 **Catàleg d'accessoris**: Vàlvules, reguladors, claus
- 💾 **Projectes**: Guarda i recupera càlculs
- 🔋 **Calculador de bateria**: Calcula bateries de bombones de propà/butà

## Tecnologies

- **Backend**: Python + Flask
- **Base de dades**: SQLite (local) / PostgreSQL (producció)
- **Frontend**: Bootstrap 5 + JavaScript
- **Desplegament**: Render.com / Railway

## Instal·lació local

```bash
git clone https://github.com/Miquel437/gaspro-web.git
cd gaspro-web
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Obre http://localhost:5000

## Desplegament a Render.com

1. Crea un compte a [Render.com](https://render.com)
2. Connecta el repositori de GitHub
3. Crea un **Web Service** amb:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Opcional: afegeix una base de dades PostgreSQL gratuïta
5. Render et donarà un enllaç com: `https://gaspro.onrender.com`
