# Aave Portfolio Dashboard

A comprehensive web application for analyzing Aave V3 lending positions across multiple blockchain networks. Built with Streamlit and integrated with the official Aave V3 GraphQL API.

## Features

- **Portfolio Overview**: Net worth, health factor, and position summaries
- **Risk Assessment**: Health factor monitoring, utilization metrics, and liquidation warnings
- **Multi-Network Support**: 18+ supported networks including Ethereum, Polygon, Arbitrum, Base, and more
- **Position Details**: Complete breakdown of supply and borrow positions
- **Visual Analytics**: Interactive charts showing portfolio distribution
- **Real-time Data**: Direct integration with Aave V3 API for live position data

## Supported Networks

- Ethereum Mainnet
- EtherFi
- Lido
- Horizon RWA
- Polygon
- Avalanche
- Arbitrum
- Base
- Optimism
- Sonic
- Metis
- Gnosis
- BNB Chain
- Scroll
- zkSync Era
- Linea
- Celo
- Soneium

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aave-portfolio-dashboard.git
cd aave-portfolio-dashboard
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `(https://aave-v3-portfolio-dashboard.streamlit.app/)`

## Usage

1. **Select Network**: Choose from the supported networks in the sidebar
2. **Enter Address**: Input any EVM-compatible wallet address
3. **Analyze Portfolio**: Click "Analyze Portfolio" to fetch and display data
4. **Review Results**: Examine portfolio overview, risk metrics, and position details

### Key Metrics Explained

- **Health Factor**: Ratio determining liquidation risk (below 1.0 = liquidation risk)
- **Utilization**: Percentage of collateral being used for borrowing
- **LTV (Loan-to-Value)**: Current borrowing ratio against collateral
- **Liquidation Threshold**: Maximum LTV before liquidation occurs
- **Net APY**: Combined yield from supplies minus borrow costs

## API Integration

This dashboard uses the official Aave V3 GraphQL API:
- **Endpoint**: `https://api.v3.aave.com/graphql`
- **Data**: Real-time user positions, market data, and account health metrics
- **Rate Limits**: Standard API rate limits apply

## Project Structure

```
aave-portfolio-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── .gitignore           # Git ignore file
```

## Key Components

### Data Classes
- `UserSupply`: Supply position data structure
- `UserBorrow`: Borrow position data structure  
- `AccountHealth`: Account health and risk metrics

### Core Functions
- `AaveDataFetcher`: API interaction class
- `display_portfolio_overview()`: Main metrics display
- `display_risk_metrics()`: Risk assessment section
- `display_positions()`: Position details tables

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push your code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository and deploy

### Alternative Deployment Options

- **Railway**: Free tier with automatic deployments
- **Render**: Free static site hosting
- **Heroku**: Cloud platform with free tier
- **Docker**: Containerized deployment

### Environment Variables

No environment variables required - the app uses public Aave API endpoints.

## Dependencies

```
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
plotly>=5.15.0
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints for new functions
- Include docstrings for public methods
- Test across multiple networks before submitting

## Limitations

- **Public Data Only**: Only displays publicly available blockchain data
- **API Dependency**: Requires Aave API availability
- **Network Coverage**: Limited to supported Aave V3 markets
- **Rate Limits**: Subject to API rate limiting during high usage

## Troubleshooting

### Common Issues

**"Invalid address format"**
- Ensure address starts with `0x` and is exactly 42 characters
- Verify the address is a valid EVM address

**"No data found"**
- Check if the address has positions on the selected network
- Try different networks where the user might be active

**"API request failed"**
- Verify internet connection
- Check if Aave API is experiencing downtime
- Try again in a few moments

### Performance Tips

- Use specific networks where you know positions exist
- Avoid rapid consecutive requests to prevent rate limiting
- Clear browser cache if experiencing display issues

## Security & Privacy

- **No Private Keys**: Only requires public wallet addresses
- **Read-Only**: Cannot execute transactions or access private data
- **No Data Storage**: Does not store user addresses or portfolio data
- **Public API**: Uses official Aave public endpoints

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Aave Protocol](https://aave.com) for the lending protocol and API
- [Streamlit](https://streamlit.io) for the web application framework
- [Plotly](https://plotly.com) for interactive charting capabilities

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section above

---

**Disclaimer**: This tool is for informational purposes only. Always verify critical financial information through official channels. The developers are not responsible for any financial decisions made based on this tool.
