from typing import Optional, List, Dict
from backend.app.schemas.market import InstrumentIdentity
from backend.app.core.currencies import get_currency_for_exchange
from backend.app.core.logging import logger


class InstrumentRegistry:
    """Maintains security identity across ticker changes, delistings, and exchanges."""

    def __init__(self):
        self._instruments: Dict[str, InstrumentIdentity] = {}
        self._symbol_index: Dict[str, str] = {}  # symbol -> instrument_id
        self._initialize_default_instruments()

    def _initialize_default_instruments(self):
        """Register default supported instruments."""
        default_instruments = [
            # India
            ("RELIANCE.NS", "NSE", "Reliance Industries Ltd", "Energy"),
            ("TCS.NS", "NSE", "Tata Consultancy Services", "Technology"),
            ("INFY.NS", "NSE", "Infosys Ltd", "Technology"),
            ("HDFCBANK.NS", "NSE", "HDFC Bank Ltd", "Financial Services"),
            ("ICICIBANK.NS", "NSE", "ICICI Bank Ltd", "Financial Services"),
            ("BHARTIARTL.NS", "NSE", "Bharti Airtel Ltd", "Telecommunications"),
            ("ITC.NS", "NSE", "ITC Ltd", "Consumer Goods"),
            ("SBIN.NS", "NSE", "State Bank of India", "Financial Services"),
            ("LTIM.NS", "NSE", "LTIMindtree Ltd", "Technology"),
            ("TATAMOTORS.NS", "NSE", "Tata Motors Ltd", "Automobiles"),
            # US
            ("AAPL", "NASDAQ", "Apple Inc", "Technology"),
            ("MSFT", "NASDAQ", "Microsoft Corporation", "Technology"),
            ("NVDA", "NASDAQ", "NVIDIA Corporation", "Technology"),
            ("GOOGL", "NASDAQ", "Alphabet Inc", "Technology"),
            ("AMZN", "NASDAQ", "Amazon.com Inc", "Consumer Discretionary"),
            ("META", "NASDAQ", "Meta Platforms Inc", "Technology"),
            ("TSLA", "NASDAQ", "Tesla Inc", "Automobiles"),
            ("AMD", "NASDAQ", "Advanced Micro Devices", "Technology"),
            ("SPY", "NYSE", "SPDR S&P 500 ETF", "ETF"),
            ("QQQ", "NASDAQ", "Invesco QQQ Trust", "ETF"),
        ]

        for symbol, exchange, name, sector in default_instruments:
            instrument_id = f"{exchange}:{symbol}"
            asset_type = "etf" if sector == "ETF" else "equity"
            instrument = InstrumentIdentity(
                instrument_id=instrument_id,
                current_symbol=symbol,
                exchange=exchange,
                asset_type=asset_type,
                company_name=name,
                currency=get_currency_for_exchange(exchange),
                sector=sector
            )
            self.register(instrument)

    def register(self, instrument: InstrumentIdentity):
        self._instruments[instrument.instrument_id] = instrument
        self._symbol_index[f"{instrument.exchange}:{instrument.current_symbol}"] = instrument.instrument_id
        for prev in instrument.previous_symbols:
            self._symbol_index[f"{instrument.exchange}:{prev}"] = instrument.instrument_id

    def get_by_id(self, instrument_id: str) -> Optional[InstrumentIdentity]:
        return self._instruments.get(instrument_id)

    def get_by_symbol(self, symbol: str, exchange: str = None) -> Optional[InstrumentIdentity]:
        if exchange:
            key = f"{exchange}:{symbol}"
            iid = self._symbol_index.get(key)
            if iid:
                return self._instruments.get(iid)
        # Search all exchanges
        for key, iid in self._symbol_index.items():
            if key.endswith(f":{symbol}"):
                return self._instruments.get(iid)
        return None

    def search(self, query: str) -> List[InstrumentIdentity]:
        query_lower = query.lower().strip()
        results = []
        for inst in self._instruments.values():
            if (query_lower in inst.current_symbol.lower() or
                query_lower in inst.company_name.lower() or
                query_lower in inst.exchange.lower() or
                any(query_lower in ps.lower() for ps in inst.previous_symbols)):
                results.append(inst)
        return results

    def mark_delisted(self, instrument_id: str, delisted_date: str):
        if instrument_id in self._instruments:
            self._instruments[instrument_id].is_delisted = True
            self._instruments[instrument_id].delisted_date = delisted_date
            logger.warning(f"Instrument {instrument_id} marked as DELISTED")

    def mark_halted(self, instrument_id: str, halted: bool = True):
        if instrument_id in self._instruments:
            self._instruments[instrument_id].is_halted = halted

    def update_symbol(self, instrument_id: str, new_symbol: str):
        if instrument_id in self._instruments:
            inst = self._instruments[instrument_id]
            old_symbol = inst.current_symbol
            inst.previous_symbols.append(old_symbol)
            inst.current_symbol = new_symbol
            # Update index
            self._symbol_index[f"{inst.exchange}:{new_symbol}"] = instrument_id
            logger.info(f"Symbol changed: {old_symbol} -> {new_symbol} for {instrument_id}")

    def get_all(self) -> List[InstrumentIdentity]:
        return list(self._instruments.values())

    def get_active(self) -> List[InstrumentIdentity]:
        return [i for i in self._instruments.values() if not i.is_delisted]


instrument_registry = InstrumentRegistry()
