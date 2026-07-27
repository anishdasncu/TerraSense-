import { useState } from 'react'
import Dashboard from './pages/Dashboard.jsx'
import Planner from './pages/Planner.jsx'
import Progress from './pages/Progress.jsx'

export default function App() {
  const [tab, setTab] = useState('dashboard')

  return (
    <div className="app">
      <header>
        <h2>TerraSense 🌍</h2>
        <nav>
          <button className={tab === 'dashboard' ? 'active' : ''} onClick={() => setTab('dashboard')}>Dashboard</button>
          <button className={tab === 'planner' ? 'active' : ''} onClick={() => setTab('planner')}>Planner</button>
          <button className={tab === 'progress' ? 'active' : ''} onClick={() => setTab('progress')}>Progress</button>
        </nav>
        <span className="leaf-icon">🍃</span>
      </header>

      {tab === 'dashboard' && (
        <div className="hero">
          <h1>🌍 Plan Your Sustainable Lifestyle</h1>
          <p>Calculate your carbon footprint, receive AI recommendations, and build greener habits.</p>
          <button onClick={() => setTab('planner')}>Start Planning</button>
        </div>
      )}

      <main>
        {tab === 'dashboard' && <Dashboard />}
        {tab === 'planner' && <Planner />}
        {tab === 'progress' && <Progress />}
      </main>
    </div>
  )
}
