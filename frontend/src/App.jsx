import { useState } from 'react'
import RestaurantMap from './components/RestaurantMap'
import Leaderboard from './components/Leaderboard'
import RecentRatings from './components/RecentRatings'
import './App.css'

function App() {
  // Which tab is currently showing — just a plain string in state, no
  // routing library needed for a handful of views.
  const [view, setView] = useState('map')

  return (
    <div className="app">
      <h1>Spice Finder</h1>
      <div className="tabs">
        <button onClick={() => setView('map')} disabled={view === 'map'}>
          Map
        </button>
        <button onClick={() => setView('leaderboard')} disabled={view === 'leaderboard'}>
          Leaderboard
        </button>
        <button onClick={() => setView('recent')} disabled={view === 'recent'}>
          Recent Ratings
        </button>
      </div>

      {view === 'map' && <RestaurantMap />}
      {view === 'leaderboard' && <Leaderboard />}
      {view === 'recent' && <RecentRatings />}
    </div>
  )
}

export default App
