import { useState, useEffect } from 'react'
import RestaurantMap from './components/RestaurantMap'
import Leaderboard from './components/Leaderboard'
import OnboardingQuiz from './components/OnboardingQuiz'
import './App.css'

function App() {
  // Which tab is currently showing — just a plain string in state, no
  // routing library needed for two views.
  const [view, setView] = useState('map')

  // null means "hasn't taken the quiz yet." We check localStorage on
  // first render so a returning visitor doesn't get the quiz again —
  // localStorage is just a small key-value store the browser keeps
  // around between visits, unlike React state which resets on refresh.
  const [spiceTolerance, setSpiceTolerance] = useState(() => {
    const saved = localStorage.getItem('spiceTolerance')
    return saved ? Number(saved) : null
  })

  function handleQuizComplete(tolerance) {
    localStorage.setItem('spiceTolerance', tolerance)
    setSpiceTolerance(tolerance)
  }
  // useState gives this component a piece of memory that persists
  // between renders. `apiStatus` is the current value, `setApiStatus`
  // is the only way you're allowed to change it. Calling setApiStatus
  // doesn't just update the variable — it tells React "re-render this
  // component, its output may have changed now."
  // Think of a component as a function that gets re-run every time its
  // state changes, and useState as the thing that lets a value survive
  // across those re-runs (a plain `let` variable would reset to its
  // initial value every re-render).
  const [apiStatus, setApiStatus] = useState('checking...')

  // useEffect runs a function after the component renders — the right
  // place for anything that reaches outside React itself, like a
  // network request. We pass an empty array [] as the second argument,
  // which means "only run this once, right after the first render" —
  // without it, this fetch would re-run after every single render,
  // which would be wasteful and could loop.
  useEffect(() => {
    fetch('/api/health')
      .then((response) => response.json())
      .then((data) => setApiStatus(data.message))
      .catch(() => setApiStatus('Could not reach the backend — is Flask running?'))
  }, [])

  if (spiceTolerance === null) {
    return (
      <div className="app">
        <h1>🌶️ Spice Finder</h1>
        <OnboardingQuiz onComplete={handleQuizComplete} />
      </div>
    )
  }

  return (
    <div className="app">
      <h1>🌶️ Spice Finder</h1>
      <p className="status-line">
        Backend status: <strong>{apiStatus}</strong>
      </p>
      <p className="status-line">
        Your spice tolerance: <strong>{spiceTolerance} / 5</strong>
      </p>
      <div className="tabs">
        <button onClick={() => setView('map')} disabled={view === 'map'}>
          Map
        </button>
        <button onClick={() => setView('leaderboard')} disabled={view === 'leaderboard'}>
          Leaderboard
        </button>
      </div>

      {view === 'map' ? <RestaurantMap /> : <Leaderboard />}
    </div>
  )
}

export default App
