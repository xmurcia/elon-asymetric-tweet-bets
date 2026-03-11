// App.js - Dashboard Principal
import React from 'react';
import GaussChart from './components/GaussChart';
import TradesTable from './components/TradesTable';
function App() { return (<div className="dashboard"><h1>Asymetric Elon Bets</h1><GaussChart /><TradesTable /></div>); }
export default App;