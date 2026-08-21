import { useState, useEffect } from 'react'
import './App.css'

function App() {
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

  return (
    <div className="app">
      <h1>🌶️ Spice Finder</h1>
      <p className="status-line">
        Backend status: <strong>{apiStatus}</strong>
      </p>
    </div>
  )
}

export default App
