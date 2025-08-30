import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from dataclasses import dataclass
import re

# Page configuration
st.set_page_config(
    page_title="Aave Portfolio Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class UserSupply:
    market_name: str
    currency_symbol: str
    currency_name: str
    balance_value: float
    balance_usd: float
    apy_formatted: str
    is_collateral: bool
    can_be_collateral: bool

@dataclass
class UserBorrow:
    market_name: str
    currency_symbol: str
    currency_name: str
    debt_value: float
    debt_usd: float
    apy_formatted: str

@dataclass
class AccountHealth:
    net_worth: float
    net_apy_formatted: str
    health_factor: float
    total_collateral_base: float
    total_debt_base: float
    available_borrows_base: float
    liquidation_threshold_formatted: str
    ltv_formatted: str
    is_in_isolation_mode: bool
    emode_enabled: bool

class AaveDataFetcher:
    def __init__(self):
        self.api_url = "https://api.v3.aave.com/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, query: str, variables: Dict = None) -> Dict:
        """Make GraphQL request to Aave API"""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_user_supplies(self, user_address: str, market_address: str, chain_id: int) -> List[UserSupply]:
        """Fetch user supplies from Aave"""
        query = """
        query GetUserSupplies($markets: [MarketInput!]!, $user: String!) {
          userSupplies(
            request: {
              markets: $markets
              user: $user
            }
          ) {
            market {
              name
              chain {
                chainId
              }
            }
            currency {
              symbol
              name
            }
            balance {
              amount {
                value
              }
              usd
            }
            apy {
              formatted
            }
            isCollateral
            canBeCollateral
          }
        }
        """
        
        variables = {
            "markets": [{"address": market_address, "chainId": chain_id}],
            "user": user_address
        }
        
        response = self._make_request(query, variables)
        
        if "errors" in response:
            raise Exception(f"GraphQL errors: {response['errors']}")
        
        supplies = []
        for supply_data in response["data"]["userSupplies"]:
            balance_value = supply_data["balance"]["amount"]["value"]
            balance_usd = supply_data["balance"]["usd"]
            
            supplies.append(UserSupply(
                market_name=supply_data["market"]["name"],
                currency_symbol=supply_data["currency"]["symbol"],
                currency_name=supply_data["currency"]["name"],
                balance_value=float(balance_value) if balance_value is not None else 0.0,
                balance_usd=float(balance_usd) if balance_usd is not None else 0.0,
                apy_formatted=supply_data["apy"]["formatted"] or "0%",
                is_collateral=supply_data["isCollateral"] or False,
                can_be_collateral=supply_data["canBeCollateral"] or False
            ))
        
        return supplies
    
    def get_user_borrows(self, user_address: str, market_address: str, chain_id: int) -> List[UserBorrow]:
        """Fetch user borrows from Aave"""
        query = """
        query GetUserBorrows($markets: [MarketInput!]!, $user: String!) {
          userBorrows(
            request: {
              markets: $markets
              user: $user
            }
          ) {
            market {
              name
              chain {
                chainId
              }
            }
            currency {
              symbol
              name
            }
            debt {
              amount {
                value
              }
              usd
            }
            apy {
              formatted
            }
          }
        }
        """
        
        variables = {
            "markets": [{"address": market_address, "chainId": chain_id}],
            "user": user_address
        }
        
        response = self._make_request(query, variables)
        
        if "errors" in response:
            raise Exception(f"GraphQL errors: {response['errors']}")
        
        borrows = []
        for borrow_data in response["data"]["userBorrows"]:
            debt_value = borrow_data["debt"]["amount"]["value"]
            debt_usd = borrow_data["debt"]["usd"]
            
            borrows.append(UserBorrow(
                market_name=borrow_data["market"]["name"],
                currency_symbol=borrow_data["currency"]["symbol"],
                currency_name=borrow_data["currency"]["name"],
                debt_value=float(debt_value) if debt_value is not None else 0.0,
                debt_usd=float(debt_usd) if debt_usd is not None else 0.0,
                apy_formatted=borrow_data["apy"]["formatted"] or "0%"
            ))
        
        return borrows
    
    def get_account_health(self, user_address: str, market_address: str, chain_id: int) -> AccountHealth:
        """Fetch user account health from Aave"""
        query = """
        query GetUserMarketState($market: String!, $user: String!, $chainId: Int!) {
          userMarketState(
            request: {
              market: $market
              user: $user
              chainId: $chainId
            }
          ) {
            netWorth
            netAPY {
              formatted
            }
            healthFactor
            eModeEnabled
            totalCollateralBase
            totalDebtBase
            availableBorrowsBase
            currentLiquidationThreshold {
              formatted
            }
            ltv {
              formatted
            }
            isInIsolationMode
          }
        }
        """
        
        variables = {
            "market": market_address,
            "user": user_address,
            "chainId": chain_id
        }
        
        response = self._make_request(query, variables)
        
        if "errors" in response:
            raise Exception(f"GraphQL errors: {response['errors']}")
        
        health_data = response["data"]["userMarketState"]
        
        net_worth = health_data.get("netWorth")
        health_factor = health_data.get("healthFactor")
        total_collateral = health_data.get("totalCollateralBase")
        total_debt = health_data.get("totalDebtBase")
        available_borrows = health_data.get("availableBorrowsBase")
        
        if health_factor == "∞" or health_factor is None:
            health_factor_value = float('inf')
        else:
            health_factor_value = float(health_factor)
        
        return AccountHealth(
            net_worth=float(net_worth) if net_worth is not None else 0.0,
            net_apy_formatted=health_data.get("netAPY", {}).get("formatted", "0%") or "0%",
            health_factor=health_factor_value,
            total_collateral_base=float(total_collateral) if total_collateral is not None else 0.0,
            total_debt_base=float(total_debt) if total_debt is not None else 0.0,
            available_borrows_base=float(available_borrows) if available_borrows is not None else 0.0,
            liquidation_threshold_formatted=health_data.get("currentLiquidationThreshold", {}).get("formatted", "0%") or "0%",
            ltv_formatted=health_data.get("ltv", {}).get("formatted", "0%") or "0%",
            is_in_isolation_mode=health_data.get("isInIsolationMode", False) or False,
            emode_enabled=health_data.get("eModeEnabled", False) or False
        )

def format_currency(amount: float) -> str:
    """Format currency amounts consistently"""
    if abs(amount) >= 1000000:
        return f"${amount/1000000:.2f}M"
    elif abs(amount) >= 1000:
        return f"${amount/1000:.1f}K"
    else:
        return f"${amount:,.2f}"

def is_valid_ethereum_address(address: str) -> bool:
    """Validate Ethereum address format"""
    pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
    return bool(pattern.match(address))

def display_portfolio_overview(health: AccountHealth, supplies: List[UserSupply], borrows: List[UserBorrow]):
    """Display consolidated portfolio overview"""
    st.subheader("Portfolio Overview")
    
    # Calculate totals
    total_supplied = sum(supply.balance_usd for supply in supplies)
    total_borrowed = sum(borrow.debt_usd for borrow in borrows)
    utilization = (health.total_debt_base / health.total_collateral_base * 100) if health.total_collateral_base > 0 else 0
    
    # Main metrics in a clean 4-column layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Net Worth", format_currency(health.net_worth))
        
    with col2:
        health_display = "∞" if health.health_factor == float('inf') else f"{health.health_factor:.2f}"
        delta_color = "normal" if health.health_factor == float('inf') or health.health_factor > 2.0 else "inverse"
        st.metric("Health Factor", health_display, 
                 help="Health Factor below 1.0 means liquidation risk")
        
    with col3:
        st.metric("Total Supplied", format_currency(total_supplied))
        
    with col4:
        st.metric("Total Borrowed", format_currency(total_borrowed))
    
    # Health warnings
    if health.health_factor != float('inf') and health.health_factor < 1.5:
        if health.health_factor < 1.0:
            st.error("LIQUIDATION RISK - Health Factor below 1.0")
        elif health.health_factor < 1.2:
            st.warning("LOW Health Factor - Consider reducing debt or adding collateral")

def display_risk_metrics(health: AccountHealth):
    """Display risk and utilization metrics"""
    st.subheader("Risk Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        utilization = (health.total_debt_base / health.total_collateral_base * 100) if health.total_collateral_base > 0 else 0
        st.metric("Utilization", f"{utilization:.1f}%")
        
    with col2:
        st.metric("Current LTV", health.ltv_formatted)
        
    with col3:
        st.metric("Liquidation Threshold", health.liquidation_threshold_formatted)
        
    with col4:
        st.metric("Net APY", health.net_apy_formatted)

def display_detailed_metrics(health: AccountHealth):
    """Display detailed financial metrics"""
    st.subheader("Detailed Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Collateral", format_currency(health.total_collateral_base))
        
    with col2:
        st.metric("Total Debt", format_currency(health.total_debt_base))
        
    with col3:
        st.metric("Available to Borrow", format_currency(health.available_borrows_base))
    
    # Status row
    st.markdown("**Account Status:**")
    status_items = []
    
    if health.emode_enabled:
        status_items.append("E-Mode Enabled")
    if health.is_in_isolation_mode:
        status_items.append("Isolation Mode Active")
    if not status_items:
        status_items.append("Normal Mode")
        
    st.write(" | ".join(status_items))

def display_supplies_table(supplies: List[UserSupply]):
    """Display supplies in a clean table format"""
    if not supplies:
        st.info("No supply positions found")
        return
    
    supply_data = []
    for supply in supplies:
        supply_data.append({
            "Asset": supply.currency_symbol,
            "Balance (USD)": format_currency(supply.balance_usd),
            "APY": supply.apy_formatted,
            "Used as Collateral": "Yes" if supply.is_collateral else "No",
            "Can be Collateral": "Yes" if supply.can_be_collateral else "No"
        })
    
    df_supplies = pd.DataFrame(supply_data)
    st.dataframe(df_supplies, use_container_width=True, hide_index=True)

def display_borrows_table(borrows: List[UserBorrow]):
    """Display borrows in a clean table format"""
    if not borrows:
        st.info("No borrow positions found")
        return
    
    borrow_data = []
    for borrow in borrows:
        borrow_data.append({
            "Asset": borrow.currency_symbol,
            "Debt (USD)": format_currency(borrow.debt_usd),
            "APY": borrow.apy_formatted
        })
    
    df_borrows = pd.DataFrame(borrow_data)
    st.dataframe(df_borrows, use_container_width=True, hide_index=True)

def display_portfolio_charts(supplies: List[UserSupply], borrows: List[UserBorrow]):
    """Display portfolio distribution charts"""
    if len(supplies) > 1 or len(borrows) > 1:
        st.subheader("Portfolio Distribution")
        
        chart_cols = st.columns(2)
        
        # Supply distribution
        if len(supplies) > 1:
            with chart_cols[0]:
                fig_supply = px.pie(
                    values=[supply.balance_usd for supply in supplies],
                    names=[supply.currency_symbol for supply in supplies],
                    title="Supply Distribution",
                    height=400
                )
                fig_supply.update_traces(textposition='inside', textinfo='percent+label')
                fig_supply.update_layout(showlegend=True, legend=dict(orientation="v"))
                st.plotly_chart(fig_supply, use_container_width=True)
        
        # Borrow distribution
        if len(borrows) > 1:
            with chart_cols[1]:
                fig_borrow = px.pie(
                    values=[borrow.debt_usd for borrow in borrows],
                    names=[borrow.currency_symbol for borrow in borrows],
                    title="Borrow Distribution",
                    height=400
                )
                fig_borrow.update_traces(textposition='inside', textinfo='percent+label')
                fig_borrow.update_layout(showlegend=True, legend=dict(orientation="v"))
                st.plotly_chart(fig_borrow, use_container_width=True)

def main():
    # Initialize session state
    if 'fetcher' not in st.session_state:
        st.session_state.fetcher = AaveDataFetcher()
    
    # Header
    st.title("Aave Portfolio Dashboard")
    st.markdown("Analyze Aave V3 positions across multiple networks")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Market selection
        market_options = {
            "Ethereum": ("0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2", 1),
            "EtherFi":("0x0AA97c284e98396202b6A04024F5E2c65026F3c0", 1),
            "Lido":("0x4e033931ad43597d96D6bcc25c280717730B58B1", 1),
            "Horizon RWA": ("0xAe05Cd22df81871bc7cC2a04BeCfb516bFe332C8", 1),
            "Polygon": ("0x794a61358d6845594f94dc1db02a252b5b4814ad", 137),
            "Avalanche": ("0x794a61358d6845594f94dc1db02a252b5b4814ad", 43114),
            "Arbitrum": ("0x794a61358d6845594f94dc1db02a252b5b4814ad", 42161),
            "Base": ("0xA238Dd80C259a72e81d7e4664a9801593F98d1c5", 8453),
            "Optimism": ("0x794a61358d6845594f94dc1db02a252b5b4814ad", 10),
            "Sonic": ("0x5362dBb1e601abF3a4c14c22ffEdA64042E5eAA3", 146),
            "Metis": ("0x90df02551bB792286e8D4f13E0e357b4Bf1D6a57", 1088),
            "Gnosis": ("0xb50201558B00496A145fE76f7424749556E326D8", 100),
            "BNB": ("0x6807dc923806fE8Fd134338EABCA509979a7e0cB", 56),
            "Scroll":("0x11fCfe756c05AD438e312a7fd934381537D3cFfe", 534352),
            "ZkSync": ("0x78e30497a3c7527d953c6B1E3541b021A98Ac43c", 324),
            "Linea": ("0xc47b8C00b0f69a36fa203Ffeac0334874574a8Ac", 59144),
            "Celo": ("0x3E59A31363E2ad014dcbc521c4a0d5757d9f3402", 42220),
            "Soneium": ("0xDd3d7A7d03D9fD9ef45f3E587287922eF65CA38B", 1868)
        }
        
        selected_market = st.selectbox("Select Network", options=list(market_options.keys()), index=0)
        market_address, chain_id = market_options[selected_market]
        
        st.markdown("---")
        st.markdown("**Features:**")
        st.markdown("• Portfolio overview with key metrics")
        st.markdown("• Risk assessment and health monitoring") 
        st.markdown("• Detailed position breakdown")
        st.markdown("• Visual portfolio distribution")
    
    # Main input section
    st.markdown("### Address Input")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_address = st.text_input(
            "EVM Address",
            placeholder="0x742d35cc6e5c4ce3b69a2a8c7c8e5f7e9a0b1234",
            help="Enter any Ethereum-compatible address"
        )
    
    with col2:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        fetch_button = st.button("Analyze Portfolio", type="primary", use_container_width=True)
    
    # Data fetching and display
    if fetch_button or (user_address and st.session_state.get('last_address') == user_address):
        if not user_address:
            st.error("Please enter an EVM address")
            return
        
        if not is_valid_ethereum_address(user_address):
            st.error("Invalid address format. Address must start with 0x and be 42 characters long.")
            return
        
        st.session_state.last_address = user_address
        
        try:
            with st.spinner(f"Fetching portfolio data from {selected_market}..."):
                supplies = st.session_state.fetcher.get_user_supplies(user_address, market_address, chain_id)
                borrows = st.session_state.fetcher.get_user_borrows(user_address, market_address, chain_id)
                health = st.session_state.fetcher.get_account_health(user_address, market_address, chain_id)
            
            st.success(f"Portfolio loaded for {user_address[:6]}...{user_address[-4:]} on {selected_market}")
            
            # Main dashboard layout
            st.markdown("---")
            
            # Portfolio Overview Section
            display_portfolio_overview(health, supplies, borrows)
            
            st.markdown("---")
            
            # Risk Metrics Section  
            display_risk_metrics(health)
            
            st.markdown("---")
            
            # Detailed Metrics Section
            display_detailed_metrics(health)
            
            st.markdown("---")
            
            # Positions Section
            st.subheader("Position Details")
            
            pos_col1, pos_col2 = st.columns(2)
            
            with pos_col1:
                st.markdown("**Supply Positions**")
                display_supplies_table(supplies)
                
            with pos_col2:
                st.markdown("**Borrow Positions**") 
                display_borrows_table(borrows)
            
            # Charts Section
            st.markdown("---")
            display_portfolio_charts(supplies, borrows)
            
        except Exception as e:
            st.error(f"Failed to fetch data: {str(e)}")
            st.info("Please verify the address has activity on the selected network and try again.")

if __name__ == "__main__":
    main()