# AI_TRADING_BOT

## Overview

**AI_TRADING_BOT** is a sophisticated trading bot specialized in Binary Options. It leverages the IQOptionAPI to execute trades and modern libraries such as `numpy`, `ta-lib`, and various technical indicators to make informed trading decisions. The bot can be packaged using `pyinstaller` for standalone executables and deployed in a `Docker` container for ease of deployment and scalability.

## Features

- **Automated Trading:** Executes trades automatically based on predefined strategies and technical indicators.
- **Technical Analysis:** Utilizes `ta-lib` and other modern libraries for comprehensive technical analysis.
- **Modular Design:** Easily customizable strategies and indicators.
- **Docker Support:** Simplified deployment using Docker.
- **Standalone Executable:** Create standalone executables using `pyinstaller`.

## Libraries and Tools

- **IQOptionAPI:** Interface for interacting with IQ Option's trading platform.
- **Numpy:** Fundamental package for numerical computations.
- **TA-Lib:** Technical Analysis Library for financial market data.
- **Indicators:** Custom and built-in indicators for trading strategies.
- **PyInstaller:** Tool for converting Python applications into standalone executables.
- **Docker:** Platform for developing, shipping, and running applications inside containers.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker
- IQ Option account

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/AI_TRADING_BOT.git
    cd AI_TRADING_BOT
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    Create a `.env` file and add your IQ Option credentials:
    ```sh
    IQ_OPTION_USERNAME=your_username
    IQ_OPTION_PASSWORD=your_password
    ```

### Usage

1. **Run the bot:**
    ```sh
    python main.py
    ```

2. **Build standalone executable:**
    ```sh
    pyinstaller --onefile main.py
    ```

3. **Run in Docker:**
    - Build the Docker image:
        ```sh
        docker build -t ai_trading_bot .
        ```
    - Run the Docker container:
        ```sh
        docker run -d --env-file .env ai_trading_bot
        ```

## Configuration

The bot configuration can be found in `config.json`. You can adjust parameters such as trading strategies, indicators, risk management settings, etc.

```json
{
    "strategy": "moving_average",
    "indicators": {
        "sma_period": 14,
        "ema_period": 9
    },
    "risk_management": {
        "max_concurrent_trades": 5,
        "risk_per_trade": 0.01
    }
}
